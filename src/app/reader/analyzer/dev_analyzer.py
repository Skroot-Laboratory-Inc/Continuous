import glob
import os.path

import numpy as np
import pandas

from src.app.helper_methods.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.model.result_set.result_set_data_point import ResultSetDataPoint
from src.app.helper_methods.model.sweep_data import SweepData
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
        self.devFilenames = self.columnFromCsv(devRunAnalyzed, 'Filename', len(self.devFiles))
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
        newPoint = ResultSetDataPoint(self.ResultSet)
        newPoint.setTime(self.devTime[self.currentDevFileIndex])
        newPoint.setDenoiseTimeSmooth(self.ResultSet.getTime() + [self.devTime[self.currentDevFileIndex]])
        newPoint.setDenoiseTime(self.ResultSet.getTime() + [self.devTime[self.currentDevFileIndex]])
        newPoint.setDenoiseFrequency(self.ResultSet.getDenoiseFrequency() + [self.devFrequency[self.currentDevFileIndex]])
        newPoint.setDenoiseFrequencySmooth(self.ResultSet.getDenoiseFrequencySmooth() + [self.devFrequency[self.currentDevFileIndex]])
        newPoint.setMaxFrequency(self.devFrequency[self.currentDevFileIndex])
        newPoint.setMaxVoltsSmooth(self.devDb[self.currentDevFileIndex])
        newPoint.setMaxFrequencySmooth(self.devFrequency[self.currentDevFileIndex])
        newPoint.setFilename(self.devFilenames[self.currentDevFileIndex])
        newPoint.setTimestamp(self.devTimestamps[self.currentDevFileIndex])
        newPoint.setDerivative(self.devFrequency[self.currentDevFileIndex])
        self.ResultSet.setValues(newPoint)

    def analyzeActualScan(self, sweepData, shouldDenoise):
        super().analyzeScan(sweepData, shouldDenoise)

    def setZeroPoint(self, zeroPoint):
        if self.DevProperties.mode == "Analysis":
            super().setZeroPoint(zeroPoint)
        else:
            self.zeroPoint = 1

    @staticmethod
    def columnFromCsvOrZero(csv, columnHeader, vectorLen, secondaryColumnHeader="", defaultValue=0):
        try:
            return csv[columnHeader].values.tolist()
        except:
            if secondaryColumnHeader != "":
                try:
                    return csv[secondaryColumnHeader].values.tolist()
                except:
                    pass
            return [defaultValue] * vectorLen

    @staticmethod
    def columnFromCsv(csv, columnHeader, vectorLen, secondaryColumnHeader=""):
        try:
            return csv[columnHeader].values.tolist()
        except:
            if secondaryColumnHeader != "":
                try:
                    return csv[secondaryColumnHeader].values.tolist()
                except:
                    pass
            return [""] * vectorLen

