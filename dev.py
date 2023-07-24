import glob
import os
import shutil

import pandas
from scipy.signal import savgol_filter


class DevMode:
    def __init__(self):
        self.devBaseFolder = r'C:\\Users\\CameronGreenwalt\\Desktop\\Calibration\\dev'
        self.tryDevMode = False
        self.fakeServer = True
        if os.path.exists(self.devBaseFolder) and self.tryDevMode:
            self.isDevMode = True
        else:
            self.isDevMode = False
        self.startTime = 400
        self.scanRate = 0.04
        self.mode = "GUI"
        # self.mode = "Analysis"


class ReaderDevMode:
    def devModeInitialization(self):
        self.DevMode = self.AppModule.DevMode
        self.AppModule.scanRate = self.DevMode.scanRate
        self.scanNumber = self.DevMode.startTime + 100000
        self.scanRate = self.DevMode.scanRate
        self.loadDevMode()

    def loadDevMode(self):
        self.devFiles = glob.glob(f'{self.DevMode.devBaseFolder}/{self.readerNumber}/*')
        readings = pandas.read_csv(rf'{self.DevMode.devBaseFolder}/{self.readerNumber}/Analyzed.csv')
        self.devTime = readings['Time (hours)'].values.tolist()
        self.devFrequency = readings['Frequency (MHz)'].values.tolist()
        try:
            self.devDb = readings['Signal Strength (dB)'].values.tolist()
        except:
            self.devDb = [0] * len(self.devFrequency)
        self.minDb = self.devDb[0:self.DevMode.startTime]
        self.minFrequency = self.devFrequency[0:self.DevMode.startTime]
        self.minDbSpline = self.devDb[0:self.DevMode.startTime]
        self.minFrequencySpline = self.devFrequency[0:self.DevMode.startTime]
        self.time = self.devTime[0:self.DevMode.startTime]
        self.minDbSmooth = self.devDb[0:self.DevMode.startTime]
        self.minFrequencySmooth = self.devFrequency[0:self.DevMode.startTime]
        self.time = self.devTime[0:self.DevMode.startTime]

    def addDevPoint(self):
        if self.DevMode.mode == "Analysis":
            try:
                nextPointIndex = len(self.time)
                self.analyzeScan(self.devFiles[nextPointIndex])
            except:
                pass
        else:
            try:
                nextPointIndex = len(self.time)
                self.addDevScan(self.devFiles[nextPointIndex])
                shutil.copy(self.devFiles[nextPointIndex], f'{self.savePath}/{self.scanNumber}.csv')
                self.minFrequency.append(self.devFrequency[nextPointIndex])
                self.time.append(self.devTime[nextPointIndex])
                self.minDb.append(self.devDb[nextPointIndex])
                self.minFrequencySpline.append(self.devFrequency[nextPointIndex])
                self.minDbSpline.append(self.devDb[nextPointIndex])
                self.minFrequencySmooth.append(self.devFrequency[nextPointIndex])
                self.minDbSmooth.append(self.devDb[nextPointIndex])
            except:
                pass

    def addDevScan(self, filename):
        readings1 = pandas.read_csv(filename)
        readings = readings1[7:-1]
        frequency = readings['Frequency(Hz)'].values.tolist()
        dB = readings['Transmission Loss(dB)'].values.tolist()
        frequency = [y / 1000000 for y in frequency]
        dB = savgol_filter(dB, 51, 2)
        self.scanFrequency, self.scanMagnitude = frequency, dB
