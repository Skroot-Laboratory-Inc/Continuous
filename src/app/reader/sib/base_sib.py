"""Base class for SIB implementations containing common functionality."""
import logging
import time
from abc import abstractmethod
from typing import List

from reactivex import Subject
from reactivex.subject import BehaviorSubject

from src.app.custom_exceptions.sib_exception import SIBReconnectException
from src.app.factory.use_case_factory import ContextFactory
from src.app.model.sweep_data import SweepData
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib_utils import (
    loadCalibrationFile,
    findSelfResonantFrequency,
    getNumPointsSweep, convertAdcToVolts, find_nearest, createCalibrationDirectoryIfNotExists, calculateFrequencyValues,
    createCalibrationFile, removeInitialSpike,
)
from src.app.widget import text_notification
from src.resources.sibcontrol import sibcontrol
from src.resources.sibcontrol.sibcontrol import SIBConnectionError, SIBTimeoutError, SIBDDSConfigError, SIBException


class BaseSib:
    """Base class for all SIB implementations with common functionality."""

    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        """Initialize common SIB properties."""
        self.PortAllocator = portAllocator
        self.readerNumber = readerNumber
        self.calibrationFrequency, self.calibrationVolts = [], []
        self.initialize(port.device)
        self.serialNumber = port.serial_number
        Properties = ContextFactory().getSibProperties()
        self.calibrationStartFreq = Properties.startFrequency
        self.calibrationStopFreq = Properties.stopFrequency
        self.stepSize = Properties.stepSize
        self.initialSpikeMhz = Properties.initialSpikeMhz
        self.calibrationFilename = calibrationFileName
        self.calibrationFilePresent = BehaviorSubject(self.loadCalibrationFile())
        self.currentlyScanning = Subject()
        self.stopFreqMHz = Properties.stopFrequency
        self.startFreqMHz = Properties.startFrequency

    @abstractmethod
    def takeScan(self, directory: str, currentVolts: float) -> SweepData:
        """The reader takes a scan and returns magnitude values. Must be implemented by subclass."""
        pass

    @staticmethod
    def getYAxisLabel() -> str:
        """Returns the y-axis label from SIB properties."""
        return ContextFactory().getSibProperties().yAxisLabel

    def loadCalibrationFile(self):
        """Load calibration file and find self-resonant frequency."""
        try:
            self.calibrationFrequency, self.calibrationVolts = loadCalibrationFile(self.calibrationFilename)
            if len(self.calibrationFrequency) == 0 or len(self.calibrationVolts) == 0:
                return False
            selfResonance = findSelfResonantFrequency(self.calibrationFrequency, self.calibrationVolts, [50, 170], 1.8)
            logging.info(f'Self resonant frequency is {selfResonance} MHz', extra={"id": f"Reader"})
            return True
        except:
            return False

    def estimateDuration(self) -> float:
        """Estimate scan duration based on number of points."""
        # Assume that the SIB can return 235 points per second or a 100-160 MHz sweep in 26s.
        return self.sib.num_pts / 235

    def performCalibration(self):
        """Perform calibration scan and load calibration file."""
        try:
            calibrationSuccessful = self.takeCalibrationScan()
            if calibrationSuccessful:
                self.calibrationFilePresent.on_next(self.loadCalibrationFile())
            return calibrationSuccessful
        except:
            return False

    def takeCalibrationScan(self) -> bool:
        try:
            self.sib.wake()
            self.currentlyScanning.on_next(True)
            createCalibrationDirectoryIfNotExists(self.calibrationFilename)
            startFrequency = self.calibrationStartFreq - self.initialSpikeMhz
            stopFrequency = self.calibrationStopFreq
            numPoints = getNumPointsSweep(startFrequency, stopFrequency)
            allFrequency = calculateFrequencyValues(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq, self.stepSize)
            self.prepareSweep(startFrequency, stopFrequency, numPoints)
            allVolts = self.performSweep()
            frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
            createCalibrationFile(self.calibrationFilename, frequency, volts)
            self.setStartFrequency(ContextFactory().getSibProperties().startFrequency)
            self.setStopFrequency(ContextFactory().getSibProperties().stopFrequency)
            return True
        except SIBConnectionError:
            self.resetSibConnection()
            raise SIBConnectionError()
        except SIBTimeoutError:
            self.resetSibConnection()
            raise SIBConnectionError()
        except SIBDDSConfigError:
            self.resetDDSConfiguration()
            raise SIBDDSConfigError()
        except SIBException:
            raise
        finally:
            self.currentlyScanning.on_next(False)
            self.sib.sleep()

    def setStartFrequency(self, startFreqMHz) -> bool:
        try:
            self.startFreqMHz = startFreqMHz - self.initialSpikeMhz
            self.sib.start_MHz = startFreqMHz - self.initialSpikeMhz
            if self.stopFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            logging.exception("Failed to set start frequency.", extra={"id": f"Sib"})
            return False

    def setStopFrequency(self, stopFreqMHz) -> bool:
        try:
            self.stopFreqMHz = stopFreqMHz
            self.sib.stop_MHz = stopFreqMHz
            if self.startFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            logging.exception("Failed to set stop frequency.", extra={"id": f"Sib"})
            return False

    def getCurrentlyScanning(self) -> Subject:
        """Returns the currently scanning subject."""
        return self.currentlyScanning

    def getCalibrationFilePresent(self) -> BehaviorSubject:
        """Returns the calibration file present behavior subject."""
        return self.calibrationFilePresent

    def setReferenceFrequency(self, peakFrequencyMHz: float):
        """Set reference frequency. Implementation varies by subclass."""
        pass

    def setNumberOfPoints(self) -> bool:
        """Set the number of points for the sweep."""
        try:
            self.sib.num_pts = getNumPointsSweep(self.startFreqMHz, self.stopFreqMHz)
            return True
        except:
            return False

    def close(self) -> bool:
        """Close the SIB connection and remove port allocation."""
        try:
            self.PortAllocator.removePort(self.readerNumber)
            self.sib.close()
            return True
        except:
            return False

    def reset(self) -> bool:
        """Reset the SIB by closing the connection."""
        return self.close()

    def initialize(self, port):
        """Initialize the SIB hardware connection."""
        self.port = port
        self.sib = sibcontrol.SIB350(port)
        self.sib.amplitude_mA = 31.6  # The synthesizer output amplitude is set to 31.6 mA by default
        self.sib.open()
        self.sib.wake()
        self.sib.write_asf()

    def performHandshake(self) -> bool:
        """Perform handshake with the SIB to establish communication."""
        data = 500332  # Some random 32-bit value
        try:
            return_val = self.sib.handshake(data)
            if return_val == data:
                self.getFirmwareVersion()
                return True
            else:
                return False
        except sibcontrol.SIBException as e:
            logging.exception("Failed to perform handshake", extra={"id": "Sib"})
            return False

    def getFirmwareVersion(self) -> str:
        """Get and log the SIB firmware version."""
        try:
            firmware_version = self.sib.version()
            logging.info(f'The SIB Firmware is version: {firmware_version}', extra={"id": "Sib"})
            return firmware_version
        except sibcontrol.SIBException as e:
            logging.exception("Failed to set firmware version", extra={"id": "Sib"})
            return ''

    def checkAndSendConfiguration(self):
        """Check and send configuration to the SIB."""
        if self.sib.valid_config():
            self.sib.write_start_ftw()  # Send the start frequency to the SIB
            self.sib.write_stop_ftw()  # Send the stop frequency to the SIB
            self.sib.write_num_pts()  # Send the number of points to the SIB
        else:
            text_notification.setText(
                f"Reader Port configuration is not valid.\nChange the scan frequency or number of points to reset it.")

    def resetDDSConfiguration(self):
        """Reset the DDS configuration after a configuration error."""
        logging.info("The DDS did not get configured correctly, performing hard reset.", extra={"id": "Sib"})
        self.sib.reset_sib()
        time.sleep(5)  # The host will need to wait until the SIB re-initializes. I do not know how long this takes.
        self.resetSibConnection()

    def resetSibConnection(self):
        """Reset the SIB connection after a communication error."""
        logging.info("Problem with serial connection. Closing and then re-opening port.", extra={"id": "Sib"})
        if self.sib.is_open():
            self.reset()
            time.sleep(1.0)
        try:
            port = self.PortAllocator.getPortForReader(self.readerNumber)
            self.initialize(port.device)
            self.setStartFrequency(self.startFreqMHz + self.initialSpikeMhz)
            self.setStopFrequency(self.stopFreqMHz)
            self.checkAndSendConfiguration()
            raise SIBReconnectException
        except SIBReconnectException:
            raise
        except:
            pass

    def performSweep(self) -> List[float]:
        self.sib.write_sweep_command()
        conversion_results, sweep_complete = list(), False
        while not sweep_complete:
            try:
                ack_msg, tmp_data = self.sib.read_sweep_response()

                if ack_msg == 'ok':
                    # SIB has sent the sweep complete command.
                    sweep_complete = True
                elif ack_msg == 'send_data':
                    # SIB is sending measurement data. Add it to the conversion results array
                    conversion_results.extend(tmp_data)
                else:
                    logging.info(f"SIB Received an unexpected command. Something is wrong. ack_msg: {ack_msg}", extra={"id": "Sib"})
            except:
                sweep_complete = True
                logging.exception("An error occurred while waiting for scan to complete", extra={"id": "Sib"})
                raise
        return convertAdcToVolts(conversion_results)

    def calibrationPointComparison(self, frequency: float, volts: float):
        calibrationVoltsOffset = find_nearest(frequency, self.calibrationFrequency, self.calibrationVolts)
        return volts / calibrationVoltsOffset

    def calibrationComparison(self, frequency, volts):
        calibratedVolts = []
        for i in range(len(frequency)):
            calibratedVolts.append(self.calibrationPointComparison(frequency[i], volts[i]))
        return calibratedVolts

    def prepareSweep(self, startFrequency, stopFrequency, numPoints):
        try:
            self.sib.start_MHz = startFrequency
            self.sib.stop_MHz = stopFrequency
            self.sib.num_pts = numPoints
            self.checkAndSendConfiguration()
        except:
            time.sleep(2)
            self.sib.start_MHz = startFrequency
            self.sib.stop_MHz = stopFrequency
            self.sib.num_pts = numPoints
            self.checkAndSendConfiguration()