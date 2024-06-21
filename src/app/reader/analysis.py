import csv
from datetime import datetime

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from src.app.exception.analysis_exception import RawScanException, SmoothedScanException
from src.app.helper.helper_functions import frequencyToIndex


class Analysis:
    def __init__(self, savePath):
        self.zeroPoint = 1

        self.timestamp = []
        self.time = []
        self.denoiseTimeSmooth = []
        self.denoiseTime = []

        self.maxVoltsSmooth = []

        self.maxFrequency = []
        self.maxFrequencySmooth = []
        self.denoiseFrequencySmooth = []
        self.denoiseFrequency = []
        self.filenames = []

        self.savePath = savePath

    def analyzeScan(self):
        try:
            maxMag, maxFreq = self.findMaximumData()
            self.maxFrequency.append(maxFreq)
        except:
            self.maxFrequency.append(np.nan)
            self.maxVoltsSmooth.append(np.nan)
            self.maxFrequencySmooth.append(np.nan)
            self.time.append((self.scanNumber - 100000) / 60)
            self.filenames.append(f"{self.scanNumber}.csv")
            self.timestamp.append(datetime.now())
            raise RawScanException()
        try:
            maxMag, maxFreq = self.findMaximumDataSmooth()
            self.maxVoltsSmooth.append(maxMag)
            self.maxFrequencySmooth.append(maxFreq)
        except:
            self.maxVoltsSmooth.append(np.nan)
            self.maxFrequencySmooth.append(np.nan)
            self.time.append((self.scanNumber - 100000) / 60)
            self.filenames.append(f"{self.scanNumber}.csv")
            self.timestamp.append(datetime.now())
            raise SmoothedScanException()
        self.time.append((self.scanNumber - 100000) / 60)
        self.filenames.append(f"{self.scanNumber}.csv")
        self.timestamp.append(datetime.now())

    def recordFailedScan(self):
        self.scanFrequency, self.scanMagnitude = [], []
        self.maxFrequency.append(np.nan)
        self.maxVoltsSmooth.append(np.nan)
        self.maxFrequencySmooth.append(np.nan)
        self.time.append((self.scanNumber - 100000) / 60)
        self.filenames.append(f"{self.scanNumber}.csv")
        self.timestamp.append(datetime.now())

    def findMaximumData(self):
        return self.findMaximum(self.scanFrequency, self.scanMagnitude)

    def findMaximumDataSmooth(self):
        if len(self.scanMagnitude) > 101:
            self.scanFrequency, self.scanMagnitude = self.scanFrequency, savgol_filter(self.scanMagnitude, 101, 2)
        else:
            self.scanFrequency, self.scanMagnitude = self.scanFrequency, self.scanMagnitude
        return self.findMaximum(self.scanFrequency, self.scanMagnitude)

    def findMaximum(self, frequency, magnitude):
        maxMag, maxFrequency = findMaxGaussian(frequency, magnitude)
        return maxMag, maxFrequency

    def denoiseResults(self):
        denoiseRadius, denoisePoints = getDenoiseParameters(self.time)
        self.denoiseTime, self.denoiseFrequency = denoise(self.time, self.maxFrequency, denoiseRadius, denoisePoints)
        self.denoiseTimeSmooth, self.denoiseFrequencySmooth = denoise(self.time, self.maxFrequencySmooth,
                                                                      denoiseRadius, denoisePoints)

    def createAnalyzedFiles(self):
        with open(f'{self.savePath}/Analyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            equilibratedY = frequencyToIndex(self.zeroPoint, self.denoiseFrequency)
            writer.writerow(['Filename', 'Time (hours)', 'Timestamp', 'Skroot Growth Index (SGI)', 'Frequency (MHz)'])
            writer.writerows(zip(self.filenames, self.denoiseTime, self.timestamp, equilibratedY, self.denoiseFrequency))
        with open(f'{self.savePath}/smoothAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            equilibratedY = frequencyToIndex(self.zeroPoint, self.denoiseFrequencySmooth)
            writer.writerow(['Filename', 'Time (hours)', 'Timestamp', 'Skroot Growth Index (SGI)', 'Frequency (MHz)'])
            writer.writerows(zip(self.filenames, self.denoiseTimeSmooth, self.timestamp, equilibratedY, self.denoiseFrequencySmooth))

    def setZeroPoint(self, zeroPoint):
        self.zeroPoint = zeroPoint

def denoise(x, y, threshold, points):
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


def getDenoiseParameters(numberOfTimePoints):
    if len(numberOfTimePoints) > 1000:
        return 0.2, 20
    elif len(numberOfTimePoints) > 100:
        return 0.5, 10
    elif len(numberOfTimePoints) > 20:
        return 0.6, 2
    else:
        return 1, 1


def gaussian(x, amplitude, centroid, peak_width):
    return amplitude * np.exp(-(x - centroid)**2 / (2 * peak_width**2))


def findMaxGaussian(x, y):
    pointsOnEachSide = 500
    if np.argmax(y) > pointsOnEachSide and np.argmax(y) < len(y)-pointsOnEachSide:
        xAroundPeak = x[np.argmax(y)-pointsOnEachSide:np.argmax(y)+pointsOnEachSide]
        yAroundPeak = y[np.argmax(y)-pointsOnEachSide:np.argmax(y)+pointsOnEachSide]
    elif np.argmax(y) > pointsOnEachSide and np.argmax(y) > len(y)-pointsOnEachSide:
        xAroundPeak = x[np.argmax(y)-pointsOnEachSide:np.argmax(y)]
        yAroundPeak = y[np.argmax(y)-pointsOnEachSide:np.argmax(y)]
    else:
        xAroundPeak = x[np.argmax(y):np.argmax(y)+pointsOnEachSide]
        yAroundPeak = y[np.argmax(y):np.argmax(y)+pointsOnEachSide]
    popt, _ = curve_fit(gaussian, xAroundPeak, yAroundPeak, p0=(max(y), x[np.argmax(y)], 1), bounds=([min(y), min(xAroundPeak), 0], [max(y), max(xAroundPeak), np.inf]))
    amplitude = popt[0]
    centroid = popt[1]
    peakWidth = popt[2]
    return amplitude, centroid