import csv
import os
import time
from bisect import bisect_left
from typing import List

import numpy as np
import pandas
import serial

import logger
import text_notification
from reader_interface import ReaderInterface


class VnaScanning(ReaderInterface):
    def __init__(self, port, AppModule, readerNumber, calibrationRequired=False):
        self.socket = serial.Serial(port, 115200, timeout=1.5)
        self.readerNumber = readerNumber
        self.AppModule = AppModule
        self.startFreqMHz = 0.1
        self.stopFreqMHz = 250
        self.nPoints = 3000
        calibrationFilename = f'{AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv'
        if calibrationRequired:
            self.takeCalibrationScan(calibrationFilename)
        self.calibrationFrequency, self.calibrationMagnitude, self.calibrationPhase = loadCalibrationFile(
            calibrationFilename)

    def takeScan(self, outputFilename) -> (List[float], List[float], List[float], bool):
        try:
            while self.AppModule.currentlyScanning:
                time.sleep(0.1)
            self.AppModule.currentlyScanning = True
            frequency, rawMagnitude, rawPhase = self.readVnaValues(self.startFreqMHz, self.stopFreqMHz, self.nPoints)
            magnitude, phase = convertAnalogToValues(rawMagnitude, rawPhase)
            calibratedMagnitude, calibratedPhase = self.calibrationComparison(frequency, magnitude, phase)
            createScanFile(outputFilename, frequency, calibratedMagnitude, calibratedPhase)
            return frequency, calibratedMagnitude, calibratedPhase, True
        except IndexError:
            # Vna returned an empty list - because it's not connected
            text_notification.setText(f"Connection lost to Reader {self.readerNumber}, check USB connection")
            logger.exception(f"Lost reader connection for reader {self.readerNumber}")
        except:
            logger.exception("Failed to take scan")
            return [], [], [], False
        finally:
            self.AppModule.currentlyScanning = False

    def takeCalibrationScan(self, calibrationFilename) -> bool:
        try:
            createCalibrationDirectoryIfNotExists(calibrationFilename)
            while self.AppModule.currentlyScanning:
                time.sleep(0.1)
            self.AppModule.currentlyScanning = True
            frequency, rawMagnitude, rawPhase = self.readVnaValues(0.1, 250, 10000)
            magnitude, phase = convertAnalogToValues(rawMagnitude, rawPhase)
            createScanFile(calibrationFilename, frequency, magnitude, phase)
            return True
        except IndexError:
            # Vna returned an empty list - because it's not connected
            text_notification.setText(
                f"Calibration Failed for reader {self.readerNumber}... \nConnection lost, check USB connection")
            logger.exception(f"Lost reader connection for reader {self.readerNumber}")
            return False
        except:
            logger.exception("Failed to take scan")
            return False
        finally:
            self.AppModule.currentlyScanning = False

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

    def setNumberOfPoints(self, nPoints):
        self.nPoints = nPoints

    def close(self):
        self.socket.close()

    """ End of required implementations, VNA specific below"""

    def readVnaValues(self, start_freq, stop_freq, num_points):
        khz2dds = 10737.4182
        df = (stop_freq - start_freq) * 1.0 / num_points
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


def loadCalibrationFile(calibrationFilename):
    try:
        readings = pandas.read_csv(calibrationFilename)
        calibrationMagnitude = list(readings['Signal Strength (dB)'].values.tolist())
        calibrationPhase = list(readings['Phase'].values.tolist())
        calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
        return calibrationFrequency, calibrationMagnitude, calibrationPhase
    except KeyError or ValueError:
        text_notification.setText("IMPORTANT!!! Software updated; calibration required.",
                                  ('Courier', 9, 'bold'), "black", "red")
        logger.exception("Column did not exist")
    except Exception:
        logger.exception("Failed to load in calibration")


def createScanFile(outputFileName, frequency, magnitude, phase):
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', 'Signal Strength (dB)', 'Phase'])
        writer.writerows(zip(frequency, magnitude, phase))
    return


def createCalibrationDirectoryIfNotExists(filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))
