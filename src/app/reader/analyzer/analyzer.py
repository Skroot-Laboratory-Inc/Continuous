import csv
import os.path
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from src.app.exception.analysis_exception import ScanAnalysisException
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import frequencyToIndex, formatDatetime, datetimeToMillis
from src.app.model.result_set.result_set import ResultSet
from src.app.model.result_set.result_set_data_point import ResultSetDataPoint
from src.app.model.sweep_data import SweepData
from src.app.reader.analyzer.analyzer_interface import AnalyzerInterface


class Analyzer(AnalyzerInterface):
    def __init__(self, FileManager: ReaderFileManager):
        self.zeroPoint = 1
        self.ResultSet = ResultSet()
        self.sweepData = SweepData([], [])
        self.FileManager = FileManager

    def analyzeScan(self, sweepData: SweepData, shouldDenoise):
        self.sweepData = sweepData
        resultSet = ResultSetDataPoint(self.ResultSet)
        resultSet.setTime((self.FileManager.getCurrentScanNumber() - 100000) / 60)
        resultSet.setFilename(os.path.basename(self.FileManager.getCurrentScan()))
        resultSet.setTimestamp(datetime.now())
        try:
            _, maxFreq = self.findMaxGaussian(sweepData.frequency, sweepData.magnitude)
            resultSet.setMaxFrequency(maxFreq)
            maxMag, maxFreq = self.findMaximumDataSmooth(sweepData)
            resultSet.setMaxVoltsSmooth(maxMag)
            resultSet.setMaxFrequencySmooth(maxFreq)
            if shouldDenoise:
                time, frequency = self.denoise(
                    self.ResultSet.getTime() + [resultSet.time],
                    self.ResultSet.getMaxFrequency() + [resultSet.maxFrequency],
                )
                resultSet.setDenoiseTime(time)
                resultSet.setDenoiseFrequency(frequency)
                time, frequency = self.denoise(
                    self.ResultSet.getTime() + [resultSet.time],
                    self.ResultSet.getMaxFrequencySmooth() + [resultSet.maxFrequencySmooth],
                )
                resultSet.setDenoiseTimeSmooth(time)
                resultSet.setDenoiseFrequencySmooth(frequency)
        except:
            raise ScanAnalysisException()
        finally:
            self.ResultSet.setValues(resultSet)

    def recordFailedScan(self):
        self.sweepData = SweepData([], [])
        resultSet = ResultSetDataPoint(self.ResultSet)
        resultSet.setTime((self.FileManager.getCurrentScanNumber() - 100000) / 60)
        resultSet.setFilename(os.path.basename(self.FileManager.getCurrentScan()))
        resultSet.setTimestamp(datetime.now())
        self.ResultSet.setValues(resultSet)

    def createAnalyzedFiles(self):
        with open(self.FileManager.getAnalyzed(), 'w', newline='') as f:
            writer = csv.writer(f)
            equilibratedY = frequencyToIndex(self.zeroPoint, self.ResultSet.getDenoiseFrequency())
            writer.writerow(['Filename', 'Time (hours)', 'Timestamp', 'Skroot Growth Index (SGI)', 'Frequency (MHz)'])
            writer.writerows(zip(
                self.ResultSet.getFilenames(),
                self.ResultSet.getDenoiseTime(),
                [formatDatetime(timestamp) for timestamp in self.ResultSet.getTimestamps()],
                equilibratedY,
                self.ResultSet.getDenoiseFrequency(),
            ))
        with open(self.FileManager.getSmoothAnalyzed(), 'w', newline='') as f:
            writer = csv.writer(f)
            equilibratedY = frequencyToIndex(self.zeroPoint, self.ResultSet.getDenoiseFrequencySmooth())
            writer.writerow(['Timestamp', 'Skroot Growth Index (SGI)'])
            writer.writerows(zip(
                [datetimeToMillis(timestamp) for timestamp in self.ResultSet.getTimestamps()],
                equilibratedY,
            ))

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
    def denoise(x, y):
        threshold, points = getDenoiseParameters(x)
        x = list(x)
        y = list(y)
        ycopy = y.copy()
        for y_index in range(len(ycopy)):
            if np.isnan(ycopy[y_index]):
                ycopy[y_index] = 0
        data = np.column_stack([x, ycopy])
        dbsc = DBSCAN(eps=threshold, min_samples=points).fit(StandardScaler().fit(data).transform(data))
        core_samples = np.zeros_like(dbsc.labels_, dtype=bool)
        core_samples[dbsc.core_sample_indices_] = True
        denoiseX = [xval for xval in x if core_samples[x.index(xval)]]
        denoiseY = [y[i] for i in range(len(y)) if core_samples[i]]
        return denoiseX, denoiseY

    @staticmethod
    def findMaxGaussian(x, y):
        pointsOnEachSide = 500
        if pointsOnEachSide < np.argmax(y) < len(y) - pointsOnEachSide:
            xAroundPeak = x[np.argmax(y) - pointsOnEachSide:np.argmax(y) + pointsOnEachSide]
            yAroundPeak = y[np.argmax(y) - pointsOnEachSide:np.argmax(y) + pointsOnEachSide]
        elif np.argmax(y) > pointsOnEachSide and np.argmax(y) > len(y) - pointsOnEachSide:
            xAroundPeak = x[np.argmax(y) - pointsOnEachSide:np.argmax(y)]
            yAroundPeak = y[np.argmax(y) - pointsOnEachSide:np.argmax(y)]
        else:
            xAroundPeak = x[np.argmax(y):np.argmax(y) + pointsOnEachSide]
            yAroundPeak = y[np.argmax(y):np.argmax(y) + pointsOnEachSide]
        popt, _ = curve_fit(
            gaussian,
            xAroundPeak,
            yAroundPeak,
            p0=(max(y), x[np.argmax(y)], 1),
            bounds=([min(y), min(xAroundPeak), 0], [max(y), max(xAroundPeak), np.inf]),
        )
        amplitude = popt[0]
        centroid = popt[1]
        peakWidth = popt[2]
        return amplitude, centroid

    @staticmethod
    def calculateDerivativeValues(time, sgi):
        cubicValues = []
        derivativeValues = []
        chunk_size = 30
        plt.scatter(time, sgi, color='tab:green', label="real data")
        for i in range(0, len(time), chunk_size):
            timeChunk = time[i:i + chunk_size]
            sgiChunk = sgi[i:i + chunk_size]
            cubicFit = np.polyfit(timeChunk, sgiChunk, 3)
            cubicFunction = np.poly1d(cubicFit)
            cubicValues = cubicValues + list(cubicFunction(timeChunk))
            derivativeFunction = np.polyder(cubicFunction)
            derivativeValues = derivativeValues + list(derivativeFunction(timeChunk))
        derivativeSmooth = list(savgol_filter(derivativeValues, 101, 2))
        return cubicValues, derivativeSmooth


def gaussian(x, amplitude, centroid, peak_width):
    return amplitude * np.exp(-(x - centroid) ** 2 / (2 * peak_width ** 2))


def getDenoiseParameters(numberOfTimePoints):
    if len(numberOfTimePoints) > 1000:
        return 0.2, 20
    elif len(numberOfTimePoints) > 100:
        return 0.5, 10
    elif len(numberOfTimePoints) > 20:
        return 0.6, 2
    else:
        return 1, 1

