import csv
import logging
import os
import time
from bisect import bisect_left
from typing import List

import numpy as np
import pandas
import serial
from serial import SerialException

import text_notification
from reader_interface import ReaderInterface


class VnaScanning(ReaderInterface):
    def __init__(self, port, calibrationFilename, readerNumber, calibrationRequired=False):
        self.calibrationFailed = False
        self.yAxisLabel = 'Signal Strength (dB)'
        try:
            self.socket = serial.Serial(port, 115200, timeout=1.5)
        except:
            self.calibrationFailed = True
        self.port = port
        self.readerNumber = readerNumber
        self.startFreqMHz = 95
        self.stopFreqMHz = 145
        self.calibrationFilename = calibrationFilename
        self.calibrationRequired = calibrationRequired
        if not calibrationRequired:
            self.loadCalibrationFile()

    def loadCalibrationFile(self):
        self.calibrationFrequency, self.calibrationMagnitude, self.calibrationPhase = loadCalibrationFile(
            self.calibrationFilename, self.yAxisLabel)

    def takeScan(self, outputFilename) -> (List[float], List[float], List[float], bool):
        try:
            frequency, rawMagnitude, rawPhase = self.readVnaValues(self.startFreqMHz, self.stopFreqMHz, self.getNumPoints())
            magnitude, phase = convertAnalogToValues(rawMagnitude, rawPhase)
            calibratedMagnitude, calibratedPhase = self.calibrationComparison(frequency, magnitude, phase)
            createScanFile(outputFilename, frequency, calibratedMagnitude, calibratedPhase, self.yAxisLabel)
            return frequency, calibratedMagnitude, calibratedPhase, True
        except IndexError:
            # Vna returned an empty list - because it's not connected
            text_notification.setText(f"Connection lost to Reader {self.readerNumber}, check USB connection")
            logging.exception(f"Lost reader connection for reader {self.readerNumber}")
        except SerialException:
            try:
                self.close()
                self.socket = serial.Serial(self.port, 115200, timeout=1.5)
                frequency, rawMagnitude, rawPhase = self.readVnaValues(self.startFreqMHz, self.stopFreqMHz, self.getNumPoints())
                magnitude, phase = convertAnalogToValues(rawMagnitude, rawPhase)
                calibratedMagnitude, calibratedPhase = self.calibrationComparison(frequency, magnitude, phase)
                createScanFile(outputFilename, frequency, calibratedMagnitude, calibratedPhase, self.yAxisLabel)
                return frequency, calibratedMagnitude, calibratedPhase, True
            except:
                logging.exception("Failed to take scan")
                return [], [], [], False
        except:
            logging.exception("Failed to take scan")
            return [], [], [], False

    def getNumPoints(self):
        return (self.stopFreqMHz - self.startFreqMHz) * 1000 / 10 + 1


    def calibrateIfRequired(self):
        if self.calibrationRequired:
            self.takeCalibrationScan()

    def takeCalibrationScan(self) -> bool:
        try:
            createCalibrationDirectoryIfNotExists(self.calibrationFilename)
            frequency, rawMagnitude, rawPhase = self.readVnaValues(49.8, 170, 10000)
            magnitude, phase = convertAnalogToValues(rawMagnitude, rawPhase)
            createScanFile(self.calibrationFilename, frequency, magnitude, phase, self.yAxisLabel)
            return True
        except IndexError:
            # Vna returned an empty list - because it's not connected
            self.calibrationFailed = True
            text_notification.setText(
                f"Calibration Failed for reader {self.readerNumber}... \nConnection lost, check USB connection")
            logging.exception(f"Lost reader connection for reader {self.readerNumber}")
            return False
        except:
            self.calibrationFailed = True
            logging.exception("Failed to take scan")
            return False

    def setStartFrequency(self, startFreqMHz):
        if 0 <= startFreqMHz <= 250 and startFreqMHz < self.stopFreqMHz:
            self.startFreqMHz = startFreqMHz
        else:
            text_notification.setText(f"Invalid value, start frequency must be between 0 and 350."
                                      f"\n start frequency not changed.")

    def setStopFrequency(self, stopFreqMHz):
        if 0 <= stopFreqMHz <= 250 and stopFreqMHz > self.startFreqMHz:
            self.stopFreqMHz = stopFreqMHz
        else:
            text_notification.setText(f"Invalid value, stop frequency must be between 0 and 350."
                                      f"\n stop frequency not changed.")


    def close(self):
        self.socket.close()

    """ End of required implementations, VNA specific below"""

    def readVnaValues(self, start_freq, stop_freq, num_points):
        khz2dds = 10737.4182
        df = (stop_freq - start_freq) / num_points
        sleep_time = 0.1
        self.socket.write(b"2\r")
        time.sleep(sleep_time)
        self.socket.write(b"%d\r" % (start_freq * 1e3 * khz2dds))
        time.sleep(sleep_time)
        self.socket.write(b"%d\r" % num_points)
        time.sleep(sleep_time)
        self.socket.write(b"%d\r" % (df * 1e3 * khz2dds))
        time.sleep(sleep_time)
        ans = b''.join(self.socket.readlines())
        a = np.frombuffer(ans, dtype=np.uint16)
        magnitude = a[1::2]
        phase = a[::2]
        frequency = start_freq + df * np.arange(0, num_points)
        return frequency, list(magnitude), list(phase)

    def calibrationComparison(self, frequency, magnitude, phase):
        calibratedMagnitude, calibratedPhase = [], []
        for i in range(len(frequency)):
            calibrationMagnitudeOffset = find_nearest(frequency[i], self.calibrationFrequency,
                                                      self.calibrationMagnitude)
            calibrationPhaseOffset = find_nearest(frequency[i], self.calibrationFrequency, self.calibrationPhase)
            calibratedMagnitude.append(
                -(convertLinearValueToDb(magnitude[i]) - convertLinearValueToDb(calibrationMagnitudeOffset)))
            calibratedPhase.append(phase[i] - calibrationPhaseOffset)
        return calibratedMagnitude, calibratedPhase


def convertLinearValueToDb(value):
    return 20 * np.log(value)


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


def convertAnalogToValues(magnitude, phase):
    magnitudeAdjusted = [mag * 1.8 / 1024 for mag in magnitude]
    phaseAdjusted = [p * np.pi / 1024 for p in phase]
    return magnitudeAdjusted, phaseAdjusted


def loadCalibrationFile(calibrationFilename, yAxisLabel):
    try:
        readings = pandas.read_csv(calibrationFilename)
        calibrationMagnitude = list(readings[yAxisLabel].values.tolist())
        calibrationPhase = list(readings['Phase'].values.tolist())
        calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
        return calibrationFrequency, calibrationMagnitude, calibrationPhase
    except KeyError or ValueError:
        logging.exception("Column did not exist")
    except Exception:
        logging.exception("Failed to load in calibration")


def createScanFile(outputFileName, frequency, magnitude, phase, yAxisLabel):
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', yAxisLabel, 'Phase'])
        writer.writerows(zip(frequency, magnitude, phase))
    return


def createCalibrationDirectoryIfNotExists(filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))
