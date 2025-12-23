import csv
import logging
import os.path
from itertools import zip_longest

import numpy as np
from scipy.signal import savgol_filter

from src.app.helper_methods.custom_exceptions.analysis_exception import ScanAnalysisException
from src.app.helper_methods.data_helpers import frequencyToIndex, findMaxGaussian
from src.app.helper_methods.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.model.result_set.result_set import ResultSet
from src.app.helper_methods.model.result_set.result_set_data_point import ResultSetDataPoint
from src.app.helper_methods.model.result_set.temperature_result_set import TemperatureResultSet
from src.app.helper_methods.model.sweep_data import SweepData
from src.app.properties.harvest_properties import HarvestProperties
from src.app.reader.algorithm.harvest_algorithm import HarvestAlgorithm


class Analyzer:
    def __init__(self, FileManager: ReaderFileManager, harvestAlgorithm: HarvestAlgorithm):
        self.zeroPoint = 1
        self.ResultSet = ResultSet()
        self.sweepData = SweepData([], [])
        self.FileManager = FileManager
        self.HarvestAlgorithm = harvestAlgorithm
        self.TemperatureResultSet = TemperatureResultSet(FileManager)

    def analyzeScan(self, sweepData: SweepData, shouldDenoise):
        self.sweepData = sweepData
        resultSet = ResultSetDataPoint(self.ResultSet)
        resultSet.setTime((self.FileManager.getCurrentScanDate() - self.ResultSet.getStartTime()) / 3600000)
        resultSet.setFilename(os.path.basename(self.FileManager.getCurrentScan()))
        resultSet.setTimestamp(self.FileManager.getCurrentScanDate())
        try:
            peakHeight, maxFreq, peakWidth = self.findMaxGaussian(sweepData.frequency, sweepData.magnitude)
            resultSet.setMaxFrequency(maxFreq)
            maxMag, maxFreq, peakWidth = self.findMaximumDataSmooth(sweepData)
            resultSet.setMaxVoltsSmooth(maxMag)
            resultSet.setMaxFrequencySmooth(maxFreq)
            resultSet.setPeakWidthSmooth(peakWidth)

            # Calculate derivative - will use denoised data if shouldDenoise is True
            # Note: We calculate this before setValues() so we use the PREVIOUS ResultSet's denoised data
            if shouldDenoise and len(self.ResultSet.getTime()) > 0:
                derivative = self.calculateDerivativeValues(
                    self.ResultSet.getDenoiseTimeSmooth(),
                    frequencyToIndex(self.zeroPoint, self.ResultSet.getDenoiseFrequencySmooth()),
                )
            else:
                derivative = self.calculateDerivativeValues(
                    [resultSet.time],
                    [frequencyToIndex(self.zeroPoint, resultSet.maxFrequency)],
                )
            resultSet.setDerivative(derivative)
            self.TemperatureResultSet.appendTemp(resultSet.timestamp)
        except:
            raise ScanAnalysisException()
        finally:
            # setValues() will calculate denoise indices based on accumulated data
            self.ResultSet.setValues(resultSet, shouldDenoise)

    def recordFailedScan(self):
        self.sweepData = SweepData([], [])
        resultSet = ResultSetDataPoint(self.ResultSet)
        resultSet.setTime((self.FileManager.getCurrentScanDate() - self.ResultSet.getStartTime()) / 3600000)
        resultSet.setFilename(os.path.basename(self.FileManager.getCurrentScan()))
        resultSet.setTimestamp(self.FileManager.getCurrentScanDate())
        self.ResultSet.setValues(resultSet, shouldDenoise=False)

    def createAnalyzedFiles(self):
        with open(self.FileManager.getAnalyzed(), 'w', newline='') as f:
            writer = csv.writer(f)
            rowHeaders = []
            rowData = []
            rowHeaders.append('Filename')
            rowData.append(self.ResultSet.getDenoiseFilenames())
            rowHeaders.append('Time (hours)')
            rowData.append(self.ResultSet.getDenoiseTime())
            rowHeaders.append('Timestamp')
            rowData.append(self.ResultSet.getDenoiseTimestamps())
            rowHeaders.append('Skroot Growth Index (SGI)')
            rowData.append(frequencyToIndex(self.zeroPoint, self.ResultSet.getDenoiseFrequency()))
            rowHeaders.append('Frequency (MHz)')
            rowData.append(self.ResultSet.getDenoiseFrequency())
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))
        with open(self.FileManager.getSmoothAnalyzed(), 'w', newline='') as f:
            writer = csv.writer(f)
            rowHeaders = []
            rowData = []
            rowHeaders.append('Timestamp')
            rowData.append(self.ResultSet.getDenoiseSmoothTimestamps())
            rowHeaders.append('Time (hours)')
            rowData.append(self.ResultSet.getDenoiseTimeSmooth())
            rowHeaders.append('Skroot Growth Index (SGI)')
            rowData.append(frequencyToIndex(self.zeroPoint, self.ResultSet.getDenoiseFrequencySmooth()))
            rowHeaders.append('Derivative')
            rowData.append(self.ResultSet.getDerivativeMean())
            rowHeaders.append('Estimated Harvest Time (hrs)')
            rowData.append(self.HarvestAlgorithm.historicalHarvestTime)
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))

    def setZeroPoint(self, zeroPoint):
        self.zeroPoint = zeroPoint

    def resetRun(self):
        self.ResultSet.resetRun()

    """ End of required public functions on future interface. """

    def findMaximumDataSmooth(self, sweepData):
        if len(sweepData.getMagnitude()) > 101:
            smoothedSweepData = SweepData(sweepData.getFrequency(), savgol_filter(sweepData.getMagnitude(), 101, 2))
            return self.findMaxGaussian(smoothedSweepData.frequency, smoothedSweepData.magnitude)
        else:
            return self.findMaxGaussian(sweepData.frequency, sweepData.magnitude)

    @staticmethod
    def findMaxGaussian(x, y) -> (float, float, float):
        """
        Find the peak using Gaussian curve fitting.
        Uses the shared findMaxGaussian helper with default 50 points on each side.
        """
        # TODO: Make pointsOnEachSide configurable since roller bottle uses 50, and others use 500
        return findMaxGaussian(x, y, pointsOnEachSide=50)

    @staticmethod
    def calculateDerivativeValues(time, sgi) -> float:
        derivativeValue = np.nan
        try:
            chunk_size = HarvestProperties().derivativePoints
            if len(time) > chunk_size:
                timeChunk = time[-chunk_size:]
                sgiChunk = sgi[-chunk_size:]

                timeChanges = []
                sgiChanges = []
                for index in range(len(timeChunk)-1):
                    sgiChanges.append(sgiChunk[index+1] - sgiChunk[index])
                    timeChanges.append(timeChunk[index+1] - timeChunk[index])
                quartile1 = np.nanquantile(sgiChanges, 0.25)
                quartile3 = np.nanquantile(sgiChanges, 0.75)
                finalSgiChanges = [sgi for sgi in sgiChanges if quartile1 < sgi < quartile3]
                derivativeValue = np.nanmean(finalSgiChanges) / np.nanmean(timeChanges)
        except:
            logging.exception("Failed to get derivative values", extra={"id": "global"})
        finally:
            return derivativeValue

