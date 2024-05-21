import glob
import os
import shutil
from datetime import datetime

import pandas
from scipy.signal import savgol_filter

from plotting import Plotting


class DevMode:
    def __init__(self):
        self.devBaseFolder = r'C:\\Users\\CameronGreenwalt\\Desktop\\Calibration\\dev'
        self.tryDevMode = False
        self.fakeServer = False
        if os.path.exists(self.devBaseFolder) and self.tryDevMode:
            self.isDevMode = True
        else:
            self.isDevMode = False
        self.startTime = 0
        self.scanRate = 0.2
        # self.mode = "GUI"
        self.mode = "Analysis"


class ReaderDevMode(Plotting):
    def __init__(self, AppModule, readerNumber):
        self.DevMode = AppModule.DevMode
        if self.DevMode.isDevMode:
            AppModule.scanRate = self.DevMode.scanRate
            self.scanNumber = self.DevMode.startTime + 100000
            self.scanRate = self.DevMode.scanRate
            self.devFiles = glob.glob(f'{self.DevMode.devBaseFolder}/{readerNumber}/*')
            readings = pandas.read_csv(rf'{self.DevMode.devBaseFolder}/{readerNumber}/smoothAnalyzed.csv')
            self.devTime = readings['Time (hours)'].values.tolist()
            try:
                self.devFrequency = readings['Frequency (MHz)'].values.tolist()
            except:
                self.devFrequency = readings['Skroot Growth Index (SGI)'].values.tolist()
            try:
                self.devDb = readings['Signal Strength (dB)'].values.tolist()
            except:
                try:
                    self.devDb = readings['Signal Strength (Unitless)'].values.tolist()
                except:
                    self.devDb = [0] * len(self.devFrequency)


            self.loadDevMode()

    def loadDevMode(self):
        self.time = self.devTime[0:self.DevMode.startTime]

        self.minFrequency = self.devFrequency[0:self.DevMode.startTime]

        self.minDbSmooth = self.devDb[0:self.DevMode.startTime]
        self.minFrequencySmooth = self.devFrequency[0:self.DevMode.startTime]

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
                self.time.append(self.devTime[nextPointIndex])
                self.timestamp.append(datetime.now())

                self.minFrequency.append(self.devFrequency[nextPointIndex])

                self.minFrequencySmooth.append(self.devFrequency[nextPointIndex])
                self.minDbSmooth.append(self.devDb[nextPointIndex])
            except:
                pass

    def addDevScan(self, filename):
        readings1 = pandas.read_csv(filename)
        readings = readings1[7:-1]
        frequency = readings['Frequency (MHz)'].values.tolist()
        dB = readings['Signal Strength (dB)'].values.tolist()
        dB = savgol_filter(dB, 51, 2)
        self.scanFrequency, self.scanMagnitude = frequency, dB
