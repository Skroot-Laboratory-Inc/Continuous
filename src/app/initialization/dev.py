import glob
import os
import shutil
from datetime import datetime

import pandas
from scipy.signal import savgol_filter

from src.app.reader.plotter import Plotter


# TODO Update this reader dev mode to be an interface of Analysis, ReaderInterface etc.
class ReaderDevMode(Plotter):
    def __init__(self, AppModule, readerNumber):
        self.DevProperties = AppModule.DevProperties
        if self.DevProperties.isDevMode:
            AppModule.scanRate = self.DevProperties.scanRate
            self.FileManager.scanNumber = self.DevProperties.startTime + 100000
            self.scanRate = self.DevProperties.scanRate
            self.devFiles = glob.glob(f'{self.DevProperties.devBaseFolder}/{readerNumber}/*')
            readings = pandas.read_csv(rf'{self.DevProperties.devBaseFolder}/{readerNumber}/smoothAnalyzed.csv')
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
        self.time = self.devTime[0:self.DevProperties.startTime]
        self.filenames = self.devFiles[0:self.DevProperties.startTime]

        self.maxFrequency = self.devFrequency[0:self.DevProperties.startTime]

        self.maxVoltsSmooth = self.devDb[0:self.DevProperties.startTime]
        self.maxFrequencySmooth = self.devFrequency[0:self.DevProperties.startTime]

    def addDevPoint(self):
        if self.DevProperties.mode == "Analysis":
            try:
                nextPointIndex = len(self.time)
                self.addDevScan(self.devFiles[nextPointIndex])
                self.analyzeScan()
                self.time[-1] = self.devTime[nextPointIndex]
            except:
                pass
        else:
            try:
                nextPointIndex = len(self.time)
                self.addDevScan(self.devFiles[nextPointIndex])
                shutil.copy(self.devFiles[nextPointIndex], self.FileManager.getCurrentScan())
                self.time.append(self.devTime[nextPointIndex])
                self.filenames.append(self.devFiles[nextPointIndex])
                self.timestamp.append(datetime.now())

                self.maxFrequency.append(self.devFrequency[nextPointIndex])

                self.maxFrequencySmooth.append(self.devFrequency[nextPointIndex])
                self.maxVoltsSmooth.append(self.devDb[nextPointIndex])
            except:
                pass

    def addDevScan(self, filename):
        readings1 = pandas.read_csv(filename)
        readings = readings1[7:-1]
        frequency = readings['Frequency (MHz)'].values.tolist()
        dB = readings['Signal Strength (dB)'].values.tolist()
        dB = savgol_filter(dB, 51, 2)
        self.scanFrequency, self.scanMagnitude = frequency, dB
