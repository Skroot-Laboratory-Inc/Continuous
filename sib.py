import csv
import logging
import os
import time
from bisect import bisect_left
from typing import List

import numpy as np
import pandas
import sibcontrol
from serial import SerialException

import logger
import text_notification
from reader_interface import ReaderInterface


class Sib(ReaderInterface):
    def __init__(self, port, calibrationFileName, readerNumber, PortAllocator, calibrationRequired=False):
        self.calibrationFailed = False
        self.yAxisLabel = 'Signal Strength (Unitless)'
        self.readerNumber = readerNumber
        self.PortAllocator = PortAllocator
        self.initialize(port)
        self.calibrationStartFreq = 50
        self.calibrationStopFreq = 170
        self.stepSize = 0.01
        self.initialSpikeMhz = 0.2
        self.calibrationFilename = calibrationFileName
        self.calibrationRequired = calibrationRequired
        if not calibrationRequired:
            self.loadCalibrationFile()

    def loadCalibrationFile(self):
        self.calibrationFrequency, self.calibrationVolts, self.calibrationPhase = loadCalibrationFile(self.calibrationFilename)

    def takeScan(self, outputFilename) -> (List[float], List[float], List[float], bool):
        try:
            allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
            allVolts = self.performSweepAndWaitForComplete()
            frequency, volts = self.removeInitialSpike(allFrequency, allVolts)
            calibratedVolts, calibratedPhase = self.calibrationComparison(frequency, volts, [])
            createScanFile(outputFilename, frequency, calibratedVolts, self.yAxisLabel)
            return frequency, volts, [], True
        except sibcontrol.SIBConnectionError:
            text_notification.setText("Failed to perform sweep for reader, resetting reader connection.")
            self.resetSibConnection()
            return [], [], [], False
        except sibcontrol.SIBTimeoutError:
            text_notification.setText("Failed to perform sweep for reader, resetting reader connection.")
            self.resetSibConnection()
            return [], [], [], False
        except sibcontrol.SIBDDSConfigError:
            text_notification.setText("Failed to perform sweep for reader, check reader connection.")
            self.resetDDSConfiguration()
            return [], [], [], False
        except sibcontrol.SIBException:
            logging.exception("Failed to perform sweep for reader with unexpected cause, check reader connection.")
            return [], [], [], False

    def removeInitialSpike(self, frequency, volts):
        pointsRemoved = int(self.initialSpikeMhz / self.stepSize)
        return frequency[pointsRemoved:], volts[pointsRemoved:]

    def calibrateIfRequired(self):
        if self.calibrationRequired:
            self.takeCalibrationScan()

    def takeCalibrationScan(self) -> bool:
        try:
            createCalibrationDirectoryIfNotExists(self.calibrationFilename)
            self.sib.start_MHz = self.calibrationStartFreq - self.initialSpikeMhz
            self.sib.stop_MHz = self.calibrationStopFreq
            self.sib.num_pts = getNumPointsSweep(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq)
            frequency = calculateFrequencyValues(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq, self.stepSize)
            volts = self.performSweepAndWaitForComplete()
            createScanFile(self.calibrationFilename, frequency, volts, self.yAxisLabel)
            return True
        except:
            self.calibrationFailed = True
            text_notification.setText("Failed to perform calibration.")
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
            return False

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

    """ End of required implementations, SIB specific below"""

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

    def checkAndSendConfiguration(self) -> bool:
        if self.sib.valid_config():
            try:
                self.sib.write_start_ftw()  # Send the start frequency ot the SIB
                self.sib.write_stop_ftw()  # Send the stop frequency to the SIB
                self.sib.write_num_pts()  # Send the number of points to the SIB
                self.sib.write_asf()  # Send the signal amplitude to the SIB
                return True
            except sibcontrol.SIBException:
                text_notification.setText("Failed to set reader configuration, check reader connection.")
                logging.exception("Failed to set reader configuration, check reader connection.")
                return False
        else:
            text_notification.setText("Reader configuration is not valid. Change the reader frequency or number of "
                                      "points.")
            return False

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

    def calibrationComparison(self, frequency, volts, phase):
        """Phase is filler for if it will be required/output for SIB or not."""
        calibratedVolts, calibratedPhase = [], []
        for i in range(len(frequency)):
            calibrationVoltsOffset = find_nearest(frequency[i], self.calibrationFrequency,
                                                  self.calibrationVolts)
            calibratedVolts.append((volts[i] / calibrationVoltsOffset))
        return calibratedVolts, calibratedPhase

    def resetDDSConfiguration(self):
        logging.info("The DDS did not get configured correctly, performing hard reset.")
        try:
            self.sib.reset_sib()
            time.sleep(5)  # The host will need to wait until the SIB re-initializes. I do not know how long this takes.
            self.resetSibConnection()
        except SerialException:
            logging.exception("Failed to reset SIB connection")

    def resetSibConnection(self):
        logging.info("Problem with serial connection. Closing and then re-opening port.")
        try:
            if self.sib.is_open():
                self.close()
                time.sleep(1.0)
            port, readerType = self.PortAllocator.getNewPort()
            self.initialize(port)
            self.setStartFrequency(self.startFreqMHz + self.initialSpikeMhz)
            self.setStopFrequency(self.stopFreqMHz)
            self.checkAndSendConfiguration()
        except sibcontrol.SIBException:
            logging.exception("Failed to reset SIB connection")


def loadCalibrationFile(calibrationFilename) -> (List[str], List[str], List[str]):
    try:
        readings = pandas.read_csv(calibrationFilename)
        calibrationVolts = list(readings['Signal Strength (V)'].values.tolist())
        calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
        return calibrationFrequency, calibrationVolts, []
    except KeyError or ValueError:
        try:
            list(readings['Signal Strength (dB)'].values.tolist())
            text_notification.setText("Calibration exists for VNA not SiB.",
                                      ('Courier', 9, 'bold'), "black", "red")
            logging.exception("Calibration found for VNA, not SiB")
        except:
            logging.exception("Column did not exist")
    except Exception:
        logging.exception("Failed to load in calibration")


def createScanFile(outputFileName, frequency, volts, yAxisLabel):
    if 'Calibration.csv' in outputFileName:
        yAxisLabel = 'Signal Strength (V)'
    else:
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
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))


def convertAdcToVolts(adcList):
    return [float(adcValue) * (3.3 / 2 ** 10) for adcValue in adcList]


def getNumPointsFrequency(startFreq, stopFreq):
    return int((stopFreq - startFreq) * 1000 / 10 + 1)


def getNumPointsSweep(startFreq, stopFreq):
    return int((stopFreq - startFreq) * 1000 / 10)

# ports = list_ports.comports()
# portNums = [int(ports[i][0][3:]) for i in range(len(ports))]
# if portNums:
#     port = f'COM{max(portNums)}'
# Sib = Sib(port)
# succeeded = Sib.performHandshake()
# resultDb = Sib.performSweep()
# firmwareVersion = Sib.getFirmwareVersion()
# Sib.sib.close()
