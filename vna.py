import csv
import time
from bisect import bisect_left

import numpy as np
import pandas
import serial

import logger


class VnaScanning:
    def __init__(self, calibrationFilename, port, AppModule, calibrationRequired=False):
        self.socket = serial.Serial(port, 115200, timeout=1.5)
        self.AppModule = AppModule
        if calibrationRequired:
            self.takeCalibrationScan(calibrationFilename)
        self.calibrationFrequency, self.calibrationMagnitude, self.calibrationPhase = loadCalibrationFile(
            calibrationFilename)

    def takeScan(self, outputFilename, startFreq, stopFreq, nPoints):
        try:
            while self.AppModule.currentlyScanning:
                time.sleep(0.1)
            self.AppModule.currentlyScanning = True
            frequency, rawMagnitude, rawPhase = self.readVnaValues(startFreq, stopFreq, nPoints)
            magnitude, phase = convertAnalogToValues(rawMagnitude, rawPhase)
            calibratedMagnitude, calibratedPhase = self.calibrationComparison(frequency, magnitude, phase)
            createScanFile(outputFilename, frequency, calibratedMagnitude, calibratedPhase)
            self.AppModule.currentlyScanning = False
            return frequency, calibratedMagnitude, calibratedPhase, True
        except:
            logger.exception("Failed to take scan")
            self.AppModule.currentlyScanning = False
            return [], [], [], False

    def takeCalibrationScan(self, calibrationFilename):
        try:
            while self.AppModule.currentlyScanning:
                time.sleep(0.1)
            self.AppModule.currentlyScanning = True
            frequency, rawMagnitude, rawPhase = self.readVnaValues(0.1, 250, 10000)
            magnitude, phase = convertAnalogToValues(rawMagnitude, rawPhase)
            createScanFile(calibrationFilename, frequency, magnitude, phase)
            self.AppModule.currentlyScanning = False
        except:
            logger.exception("Failed to take scan")
            self.AppModule.currentlyScanning = False

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
            calibrationMagnitudeOffset = find_nearest(frequency[i], self.calibrationFrequency, self.calibrationMagnitude)
            calibrationPhaseOffset = find_nearest(frequency[i], self.calibrationFrequency, self.calibrationPhase)
            calibratedMagnitude.append(
                -(convertLinearValueToDb(magnitude[i]) - convertLinearValueToDb(calibrationMagnitudeOffset)))
            calibratedPhase.append(convertLinearValueToDb(phase[i]) - convertLinearValueToDb(calibrationPhaseOffset))
        return calibratedMagnitude, calibratedPhase

    def closeSocket(self):
        self.socket.close()


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
    readings = pandas.read_csv(calibrationFilename)
    calibrationMagnitude = list(readings['Signal Strength (dB)'].values.tolist())
    calibrationPhase = list(readings['Phase'].values.tolist())
    calibrationFrequency = readings['Frequency (MHz)'].values.tolist()
    return calibrationFrequency, calibrationMagnitude, calibrationPhase


def createScanFile(outputFileName, frequency, magnitude, phase):
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', 'Signal Strength (dB)', 'Phase'])
        writer.writerows(zip(frequency, magnitude, phase))
    return
