import glob
import os.path

import numpy as np
import pandas

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.model.sweep_data import SweepData
from src.app.properties.dev_properties import DevProperties
from src.app.reader.algorithm.harvest_algorithm import HarvestAlgorithm
from src.app.reader.analyzer.analyzer import Analyzer


class DevAnalyzer(Analyzer):
    """
    DevAnalyzer uses all the functions in Analyzer but overwrites AnalyzeScan to pull from static files depending
    on the dev mode.
    """
    def __init__(self, FileManager: ReaderFileManager, readerNumber, harvestAlgorithm: HarvestAlgorithm):
        super().__init__(FileManager, harvestAlgorithm)

        self.DevProperties = DevProperties()
        self.FileManager.scanNumber = self.DevProperties.startTime + 100000
        self.devFiles = glob.glob(f'{self.DevProperties.devBaseFolder}/Reader {readerNumber}/1*.csv')
        devRunAnalyzed = pandas.read_csv(rf'{self.DevProperties.devBaseFolder}/Reader {readerNumber}/smoothAnalyzed.csv')
        self.devTime = self.columnFromCsvOrZero(devRunAnalyzed, 'Time (hours)', len(self.devFiles))
        self.devTimestamps = self.columnFromCsvOrZero(devRunAnalyzed, 'Timestamp', len(self.devFiles))
        self.devFilenames = self.columnFromCsvOrZero(devRunAnalyzed, 'Filename', len(self.devFiles))
        self.devFrequency = self.columnFromCsvOrZero(
            devRunAnalyzed,
            'Frequency (MHz)',
            len(self.devFiles),
            'Skroot Growth Index (SGI)'
        )
        self.devDb = self.columnFromCsvOrZero(devRunAnalyzed, 'Signal Strength (Unitless)', len(self.devFiles))
        _, self.currentDevFile = next(
            (x, val) for x, val in enumerate(self.devFiles)
            if float(os.path.basename(val)[0:-4]) > self.DevProperties.startTime + 100000
        )
        self.currentDevFileIndex, _ = next(
            (x, val) for x, val in enumerate(self.devTime)
            if val*60 > self.DevProperties.startTime
        )
        self.loadDevMode()

    def analyzeScan(self, sweepData: SweepData, shouldDenoise):
        self.sweepData = sweepData
        self.currentDevFileIndex += 1
        if self.DevProperties.mode == "Analysis":
            self.analyzeActualScan(sweepData, shouldDenoise)
        else:
            self.analyzeDevScan()

    """ Private dev functions """

    def loadDevMode(self):
        self.ResultSet.time = self.devTime[0:self.currentDevFileIndex]
        self.ResultSet.denoiseTime = self.devTime[0:self.currentDevFileIndex]
        self.ResultSet.denoiseTimeSmooth = self.devTime[0:self.currentDevFileIndex]
        self.ResultSet.timestamps = self.devTimestamps[0:self.currentDevFileIndex]
        self.ResultSet.filenames = self.devFilenames[0:self.currentDevFileIndex]
        self.ResultSet.smoothDerivativeMean = [np.nan for _ in self.devTime[0:self.currentDevFileIndex]]
        self.ResultSet.derivativeMean = [np.nan for _ in self.devTime[0:self.currentDevFileIndex]]
        self.ResultSet.derivative = [np.nan for _ in self.devTime[0:self.currentDevFileIndex]]
        self.ResultSet.peakWidthsSmooth = [np.nan for _ in self.devTime[0:self.currentDevFileIndex]]

        self.ResultSet.maxVoltsSmooth = self.devDb[0:self.currentDevFileIndex]

        self.ResultSet.maxFrequency = self.devFrequency[0:self.currentDevFileIndex]
        self.ResultSet.denoiseFrequency = self.devFrequency[0:self.currentDevFileIndex]
        self.ResultSet.maxFrequencySmooth = self.devFrequency[0:self.currentDevFileIndex]
        self.ResultSet.denoiseFrequencySmooth = self.devFrequency[0:self.currentDevFileIndex]

    def analyzeDevScan(self):
        self.ResultSet.time.append(self.devTime[self.currentDevFileIndex])
        self.ResultSet.denoiseTimeSmooth.append(self.devTime[self.currentDevFileIndex])
        self.ResultSet.timestamps.append(self.devTimestamps[self.currentDevFileIndex])
        self.ResultSet.filenames.append(self.devFilenames[self.currentDevFileIndex])

        self.ResultSet.maxVoltsSmooth.append(self.devDb[self.currentDevFileIndex])

        self.ResultSet.maxFrequency.append(self.devFrequency[self.currentDevFileIndex])
        self.ResultSet.denoiseFrequency.append(self.devFrequency[self.currentDevFileIndex])
        self.ResultSet.maxFrequencySmooth.append(self.devFrequency[self.currentDevFileIndex])
        self.ResultSet.denoiseFrequencySmooth.append(self.devFrequency[self.currentDevFileIndex])

    def analyzeActualScan(self, sweepData, shouldDenoise):
        super().analyzeScan(sweepData, shouldDenoise)

    def setZeroPoint(self, zeroPoint):
        # TODO When using mode "GUI" SGI calculations are taken on the already SGI values. Needs fixing
        if self.DevProperties.mode == "Analysis":
            super().setZeroPoint(zeroPoint)
        else:
            self.zeroPoint = 1

    @staticmethod
    def columnFromCsvOrZero(csv, columnHeader, vectorLen, secondaryColumnHeader=""):
        try:
            return csv[columnHeader].values.tolist()
        except:
            if secondaryColumnHeader != "":
                try:
                    return csv[secondaryColumnHeader].values.tolist()
                except:
                    pass
            return [0] * vectorLen

