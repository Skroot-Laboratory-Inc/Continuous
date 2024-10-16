import csv
import logging
import os
import time
from bisect import bisect_left
from typing import List

import numpy as np
import pandas
import sibcontrol
from sibcontrol import SIBConnectionError, SIBTimeoutError, SIBException, SIBDDSConfigError

from src.app.exception.sib_exception import SIBReconnectException
from src.app.helper import helper_functions
from src.app.model.sweep_data import SweepData
from src.app.properties.common_properties import CommonProperties
from src.app.properties.sib_properties import SibProperties
from src.app.reader.sib.sib_interface import SibInterface
from src.app.widget import text_notification


class Sib(SibInterface):
    def __init__(self, port, calibrationFileName, readerNumber, PortAllocator, calibrationRequired=False):
        self.calibrationFailed = False
        self.readerNumber = readerNumber
        self.PortAllocator = PortAllocator
        self.initialize(port.device)
        self.serialNumber = port.serial_number
        Properties = SibProperties()
        self.calibrationStartFreq = Properties.calibrationStartFreq
        self.calibrationStopFreq = Properties.calibrationStopFreq
        self.stepSize = Properties.stepSize
        self.initialSpikeMhz = Properties.initialSpikeMhz
        self.yAxisLabel = Properties.yAxisLabel
        self.calibrationFilename = calibrationFileName
        self.calibrationRequired = calibrationRequired
        self.stopFreqMHz = None
        self.startFreqMHz = None
        if not calibrationRequired:
            self.loadCalibrationFile()

    def getYAxisLabel(self) -> str:
        return self.yAxisLabel

    def loadCalibrationFile(self):
        self.calibrationFrequency, self.calibrationVolts = loadCalibrationFile(self.calibrationFilename)
        selfResonance = findSelfResonantFrequency(self.calibrationFrequency, self.calibrationVolts, [50, 170], 1.8)
        logging.info(f'Self resonant frequency for reader {self.readerNumber} is {selfResonance} MHz')

    def takeScan(self, outputFilename, disableSaveFiles) -> SweepData:
        try:
            allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
            allVolts = self.performSweepAndWaitForComplete()
            frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
            calibratedVolts = self.calibrationComparison(frequency, volts)
            if not disableSaveFiles:
                createScanFile(outputFilename, frequency, calibratedVolts, self.yAxisLabel)
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

    def calibrateIfRequired(self):
        if self.calibrationRequired:
            self.takeCalibrationScan()
        self.loadCalibrationFile()

    def takeCalibrationScan(self) -> bool:
        try:
            createCalibrationDirectoryIfNotExists(self.calibrationFilename)
            self.sib.start_MHz = self.calibrationStartFreq - self.initialSpikeMhz
            self.sib.stop_MHz = self.calibrationStopFreq
            self.sib.num_pts = getNumPointsSweep(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq)
            allFrequency = calculateFrequencyValues(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq, self.stepSize)
            allVolts = self.performSweepAndWaitForComplete()
            frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
            createScanFile(self.calibrationFilename, frequency, volts, self.yAxisLabel)
            self.setStartFrequency(CommonProperties().defaultStartFrequency)
            self.setStopFrequency(CommonProperties().defaultEndFrequency)
            return True
        except:
            self.calibrationFailed = True
            text_notification.setText(f"Failed to perform calibration for reader {self.readerNumber}.")
            logging.exception("Failed to perform calibration.")
            return False

    def setStartFrequency(self, startFreqMHz) -> bool:
        try:
            self.startFreqMHz = startFreqMHz - self.initialSpikeMhz
            self.sib.start_MHz = startFreqMHz - self.initialSpikeMhz
            if self.stopFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            text_notification.setText("Failed to set start frequency.")
            logging.exception("Failed to set start frequency.")
            return False

    def setStopFrequency(self, stopFreqMHz) -> bool:
        try:
            self.stopFreqMHz = stopFreqMHz
            self.sib.stop_MHz = stopFreqMHz
            if self.startFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            text_notification.setText("Failed to set stop frequency.")
            logging.exception("Failed to set stop frequency.")
            return False

    """ End of required implementations, SIB specific below"""

    def setNumberOfPoints(self) -> bool:
        try:
            self.sib.num_pts = getNumPointsSweep(self.startFreqMHz, self.stopFreqMHz)
            return True
        except:
            return False

    def close(self) -> bool:
        try:
            self.PortAllocator.removePort(self.port)
            self.sib.close()
            return True
        except:
            return False

    def reset(self) -> bool:
        try:
            self.sib.close()
            return True
        except:
            return False

    def initialize(self, port):
        self.port = port
        self.sib = sibcontrol.SIB350(port)
        self.sib.amplitude_mA = 31.6  # The synthesizer output amplitude is set to 31.6 mA by default
        self.sib.open()

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
            logging.exception("Failed to perform handshake")
            return False

    def getFirmwareVersion(self) -> str:
        try:
            firmware_version = self.sib.version()
            logging.info(f'The SIB Firmware is version: {firmware_version}')
            return firmware_version
        except sibcontrol.SIBException as e:
            logging.exception("Failed to set firmware version")
            return ''

    def sleep(self) -> None:
        self.sib.sleep()

    def wake(self) -> None:
        self.sib.wake()

    def checkAndSendConfiguration(self):
        if self.sib.valid_config():
            self.sib.write_start_ftw()  # Send the start frequency ot the SIB
            self.sib.write_stop_ftw()  # Send the stop frequency to the SIB
            self.sib.write_num_pts()  # Send the number of points to the SIB
            self.sib.write_asf()  # Send the signal amplitude to the SIB
        else:
            text_notification.setText(f"Reader {self.readerNumber} configuration is not valid. Change the reader frequency or number of "
                                      "points.")

    def performSweepAndWaitForComplete(self) -> List[str]:
        self.checkAndSendConfiguration()
        self.wake()
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
                    logging.info(f"SIB Received an unexpected command. Something is wrong. ack_msg: {ack_msg}")
            except:
                sweep_complete = True
                logging.exception("An error occurred while waiting for scan to complete")
                raise
        self.sleep()
        return convertAdcToVolts(conversion_results)

    def calibrationComparison(self, frequency, volts):
        calibratedVolts = []
        for i in range(len(frequency)):
            calibrationVoltsOffset = find_nearest(frequency[i], self.calibrationFrequency,
                                                  self.calibrationVolts)
            calibratedVolts.append((volts[i] / calibrationVoltsOffset))
        return calibratedVolts

    def resetDDSConfiguration(self):
        logging.info("The DDS did not get configured correctly, performing hard reset.")
        self.sib.reset_sib()
        time.sleep(5)  # The host will need to wait until the SIB re-initializes. I do not know how long this takes.
        self.resetSibConnection()

    def resetSibConnection(self):
        logging.info("Problem with serial connection. Closing and then re-opening port.")
        if self.sib.is_open():
            self.reset()
            time.sleep(1.0)
        try:
            port = self.PortAllocator.getMatchingPort(self.serialNumber)
            self.initialize(port)
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
        logging.exception("Column did not exist")
    except Exception:
        logging.exception("Failed to load in calibration")


def createScanFile(outputFileName, frequency, volts, yAxisLabel):
    if 'Calibration.csv' in outputFileName:
        yAxisLabel = 'Signal Strength (V)'
    else:
        volts = helper_functions.convertListToPercent(volts)
        yAxisLabel = yAxisLabel
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', yAxisLabel])
        writer.writerows(zip(frequency, volts))
    return


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
    inRangeFrequencies, inRangeVolts = helper_functions.truncateByX(scanRange[0], scanRange[1], frequency, volts)
    for index, yval in enumerate(inRangeVolts):
        if yval > threshold:
            return inRangeFrequencies[index]


def removeInitialSpike(frequency, volts, initialSpikeMhz, stepSize):
    pointsRemoved = int(initialSpikeMhz / stepSize)
    return frequency[pointsRemoved:], volts[pointsRemoved:]
