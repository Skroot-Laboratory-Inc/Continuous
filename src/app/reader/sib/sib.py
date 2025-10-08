import csv
import logging
import os
import time
from bisect import bisect_left
from typing import List

import numpy as np
import pandas
from reactivex import Subject
from reactivex.subject import BehaviorSubject

from src.app.custom_exceptions.sib_exception import SIBReconnectException
from src.app.helper_methods.data_helpers import truncateByX
from src.app.model.sweep_data import SweepData
from src.app.properties.common_properties import CommonProperties
from src.app.properties.sib_properties import SibProperties
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib_interface import SibInterface
from src.app.widget import text_notification
from src.resources.sibcontrol import sibcontrol
from src.resources.sibcontrol.sibcontrol import SIBDDSConfigError, SIBException, SIBConnectionError, SIBTimeoutError


class Sib(SibInterface):
    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        self.PortAllocator = portAllocator
        self.readerNumber = readerNumber
        self.calibrationFrequency, self.calibrationVolts = [], []
        self.initialize(port.device)
        self.serialNumber = port.serial_number
        Properties = SibProperties()
        self.calibrationStartFreq = Properties.calibrationStartFreq
        self.calibrationStopFreq = Properties.calibrationStopFreq
        self.stepSize = Properties.stepSize
        self.initialSpikeMhz = Properties.initialSpikeMhz
        self.calibrationFilename = calibrationFileName
        self.stopFreqMHz = None
        self.startFreqMHz = None
        self.calibrationFilePresent = BehaviorSubject(self.loadCalibrationFile())
        self.currentlyScanning = Subject()

    def getYAxisLabel(self) -> str:
        return SibProperties().yAxisLabel

    def loadCalibrationFile(self):
        try:
            self.calibrationFrequency, self.calibrationVolts = loadCalibrationFile(self.calibrationFilename)
            if len(self.calibrationFrequency) == 0 or len(self.calibrationVolts) == 0:
                return False
            selfResonance = findSelfResonantFrequency(self.calibrationFrequency, self.calibrationVolts, [50, 170], 1.8)
            logging.info(f'Self resonant frequency is {selfResonance} MHz', extra={"id": f"Reader"})
            return True
        except:
            return False

    def takeScan(self, outputFilename, disableSaveFiles) -> SweepData:
        try:
            allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
            allVolts = self.performSweepAndWaitForComplete()
            frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
            calibratedVolts = self.calibrationComparison(frequency, volts)
            return SweepData(frequency, calibratedVolts)
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

    def estimateDuration(self) -> float:
        # Assume that the SIB can return 235 points per second or a 100-160 MHz sweep in 26s.
        return self.sib.num_pts / 235

    def performCalibration(self):
        try:
            calibrationSuccessful = self.takeCalibrationScan()
            if calibrationSuccessful:
                self.calibrationFilePresent.on_next(self.loadCalibrationFile())
            return calibrationSuccessful
        except:
            return False

    def takeCalibrationScan(self) -> bool:
        try:
            self.currentlyScanning.on_next(True)
            createCalibrationDirectoryIfNotExists(self.calibrationFilename)
            self.sib.start_MHz = self.calibrationStartFreq - self.initialSpikeMhz
            self.sib.stop_MHz = self.calibrationStopFreq
            self.sib.num_pts = getNumPointsSweep(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq)
            allFrequency = calculateFrequencyValues(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq, self.stepSize)
            allVolts = self.performSweepAndWaitForComplete()
            frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
            createCalibrationFile(self.calibrationFilename, frequency, volts)
            self.setStartFrequency(CommonProperties().defaultStartFrequency)
            self.setStopFrequency(CommonProperties().defaultEndFrequency)
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

    def setStartFrequency(self, startFreqMHz) -> bool:
        try:
            self.startFreqMHz = startFreqMHz - self.initialSpikeMhz
            self.sib.start_MHz = startFreqMHz - self.initialSpikeMhz
            if self.stopFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            text_notification.setText("Reader hardware disconnected.\nPlease contact your system administrator.")
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
            text_notification.setText("Reader hardware disconnected.\nPlease contact your system administrator.")
            logging.exception("Failed to set stop frequency.", extra={"id": f"Sib"})
            return False

    def getCurrentlyScanning(self) -> Subject:
        return self.currentlyScanning

    def getCalibrationFilePresent(self) -> BehaviorSubject:
        return self.calibrationFilePresent

    """ End of required implementations, SIB specific below"""

    def setNumberOfPoints(self) -> bool:
        try:
            self.sib.num_pts = getNumPointsSweep(self.startFreqMHz, self.stopFreqMHz)
            return True
        except:
            return False

    def close(self) -> bool:
        try:
            self.PortAllocator.removePort(self.readerNumber)
            self.sib.close()
            return True
        except:
            return False

    def reset(self) -> bool:
        return self.close()

    def initialize(self, port):
        self.port = port
        self.sib = sibcontrol.SIB350(port)
        self.sib.amplitude_mA = 31.6  # The synthesizer output amplitude is set to 31.6 mA by default
        self.sib.open()
        self.sib.wake()

    def performHandshake(self) -> bool:
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
        try:
            firmware_version = self.sib.version()
            logging.info(f'The SIB Firmware is version: {firmware_version}', extra={"id": "Sib"})
            return firmware_version
        except sibcontrol.SIBException as e:
            logging.exception("Failed to set firmware version", extra={"id": "Sib"})
            return ''

    def checkAndSendConfiguration(self):
        if self.sib.valid_config():
            self.sib.write_start_ftw()  # Send the start frequency ot the SIB
            self.sib.write_stop_ftw()  # Send the stop frequency to the SIB
            self.sib.write_num_pts()  # Send the number of points to the SIB
            self.sib.write_asf()  # Send the signal amplitude to the SIB
        else:
            text_notification.setText(
                f"Reader configuration is not valid. Change the reader frequency or number of points.")

    def performSweepAndWaitForComplete(self) -> List[str]:
        self.checkAndSendConfiguration()
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

    def calibrationComparison(self, frequency, volts):
        calibratedVolts = []
        for i in range(len(frequency)):
            calibrationVoltsOffset = find_nearest(frequency[i], self.calibrationFrequency,
                                                  self.calibrationVolts)
            calibratedVolts.append((volts[i] / calibrationVoltsOffset))
        return calibratedVolts

    def resetDDSConfiguration(self):
        logging.info("The DDS did not get configured correctly, performing hard reset.", extra={"id": "Sib"})
        self.sib.reset_sib()
        time.sleep(5)  # The host will need to wait until the SIB re-initializes. I do not know how long this takes.
        self.resetSibConnection()

    def resetSibConnection(self):
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


def loadCalibrationFile(calibrationFilename) -> (List[str], List[str], List[str]):
    try:
        readings = pandas.read_csv(calibrationFilename)
        calibrationVolts = list(readings['Signal Strength (V)'].values.tolist())
        calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
        return calibrationFrequency, calibrationVolts
    except KeyError or ValueError:
        logging.exception("Column did not exist", extra={"id": calibrationFilename})
        return [], []
    except FileNotFoundError:
        logging.exception("No previous calibration found.", extra={"id": calibrationFilename})
        text_notification.setText("No previous calibration found, please calibrate.")
        return [], []
    except Exception:
        logging.exception("Failed to load in calibration", extra={"id": calibrationFilename})
        return [], []


def createCalibrationFile(outputFileName, frequency, volts):
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', 'Signal Strength (V)'])
        writer.writerows(zip(frequency, volts))


def calculateFrequencyValues(startFreqMHz, stopFreqMHz, df) -> List[str]:
    nPoints = getNumPointsFrequency(startFreqMHz, stopFreqMHz)
    return startFreqMHz + df * np.arange(0, nPoints)


def find_nearest(freq, freqList, dBlist):
    pos = bisect_left(freqList, freq)
    if pos == 0:
        return dBlist[0]
    if pos == len(freqList):
        return dBlist[-1]
    before = freqList[pos - 1]
    after = freqList[pos]
    if after - freq < freq - before:
        return dBlist[pos]
    else:
        return dBlist[pos - 1]


def createCalibrationDirectoryIfNotExists(filename):
    if not os.path.exists(os.path.dirname(os.path.dirname(filename))):
        os.mkdir(os.path.dirname(os.path.dirname(filename)))
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))


def convertAdcToVolts(adcList):
    return [float(adcValue) * (3.3 / 2 ** 10) for adcValue in adcList]


def getNumPointsFrequency(startFreq, stopFreq):
    return int((stopFreq - startFreq) * 1000 / 10 + 1)


def getNumPointsSweep(startFreq, stopFreq):
    return int((stopFreq - startFreq) * 1000 / 10)


def findSelfResonantFrequency(frequency, volts, scanRange, threshold):
    inRangeFrequencies, inRangeVolts = truncateByX(scanRange[0], scanRange[1], frequency, volts)
    for index, yval in enumerate(inRangeVolts):
        if yval > threshold:
            return inRangeFrequencies[index]


def removeInitialSpike(frequency, volts, initialSpikeMhz, stepSize):
    pointsRemoved = int(initialSpikeMhz / stepSize)
    return frequency[pointsRemoved:], volts[pointsRemoved:]
