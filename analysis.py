import csv
import warnings
from datetime import datetime
from statistics import mean

import numpy as np
import pandas
from scipy.interpolate import CubicSpline
from scipy.signal import savgol_filter
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

import logger
from exceptions import badFit


class Analysis:
    def __init__(self, savePath, smallPeakPoints, largePeakPoints):
        self.zeroPoint = 0
        self.denoiseFrequencySmooth = []
        self.denoiseTimeSmooth = []
        self.denoiseTotalMinSmooth = []
        self.denoiseTimeDbSmooth = []
        self.denoiseTime = []
        self.denoiseTimeDb = []
        self.denoiseFrequency = []
        self.denoiseTotalMin = []
        self.savePath = savePath
        self.minFrequency = []
        self.minFrequencySpline = []
        self.minFrequencyRaw = []
        self.minFrequencySmooth = []
        self.minDb = []
        self.minDbSpline = []
        self.minDbRaw = []
        self.minDbSmooth = []
        self.time = []
        self.timestamp = []
        self.smallPeakPoints = smallPeakPoints
        self.largePeakPoints = largePeakPoints

    def analyzeScan(self, filename):
        minMag, minFreq, rawMinMag, rawMinFreq = self.findMinData(filename)
        self.minDb.append(minMag)
        self.minFrequency.append(minFreq)
        self.minDbRaw.append(minMag)
        self.minFrequencyRaw.append(minFreq)
        minMag, minFreq, _, _ = self.findMinDataSmooth(filename)
        self.minDbSmooth.append(minMag)
        self.minFrequencySmooth.append(minFreq)
        minMag, minFreq = findMinDataSpline(filename)
        self.minDbSpline.append(minMag)
        self.minFrequencySpline.append(minFreq)
        self.time.append((self.scanNumber - 100000) / 60)
        self.timestamp.append(datetime.now())

    def findMinData(self, filename):
        self.scanFrequency, self.scanMagnitude = extractValuesFromScanFile(filename)
        return self.findMin(self.scanFrequency, self.scanMagnitude)

    def findMinDataSmooth(self, filename):
        frequency, magnitude = extractValuesFromScanFile(filename)
        self.scanFrequency, self.scanMagnitude = frequency, savgol_filter(magnitude, 501, 2)
        return self.findMin(frequency, self.scanMagnitude)

    def findMin(self, frequency, magnitude):
        try:
            minimumIndex, rawFrequencyMinimum, rawMagnitudeMinimum = findRawMinimum(frequency, magnitude)
            points = self.determineFitPoints()
            quadraticFrequency = frequency[minimumIndex - points:minimumIndex + points]
            quadraticMagnitude = magnitude[minimumIndex - points:minimumIndex + points]
            minMag, minFrequency = findQuadraticMinimum(quadraticFrequency, quadraticMagnitude, rawMagnitudeMinimum,
                                                        points)
            return minMag, minFrequency, rawMagnitudeMinimum, rawFrequencyMinimum
        except:
            logger.exception("Failed to analyze scan")
            return np.nan, np.nan, np.nan, np.nan

    def denoiseResults(self):
        denoiseRadius, denoisePoints = getDenoiseParameters(self.time)
        self.denoiseTime, self.denoiseFrequency = denoise(self.time, self.minFrequency, denoiseRadius, denoisePoints)
        self.denoiseTimeSmooth, self.denoiseFrequencySmooth = denoise(self.time, self.minFrequencySmooth,
                                                                      denoiseRadius, denoisePoints)
        self.denoiseTimeDb, self.denoiseTotalMin = denoise(self.time, self.minDb, denoiseRadius, denoisePoints)
        self.denoiseTimeDbSmooth, self.denoiseTotalMinSmooth = denoise(self.time, self.minDbSmooth,
                                                                       denoiseRadius, denoisePoints)

    def createAnalyzedFiles(self):
        with open(f'{self.savePath}/Analyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Timestamp', 'Skroot Growth Index (SGI)', 'Signal Strength (dB)'])
            writer.writerows(zip(self.time, self.timestamp, self.frequencyToIndex(self.minFrequency), self.minDb))
        with open(f'{self.savePath}/smoothAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Timestamp', 'Skroot Growth Index (SGI)', 'Signal Strength (dB)'])
            writer.writerows(zip(self.time, self.timestamp, self.frequencyToIndex(self.minFrequencySmooth), self.minDbSmooth))
        with open(f'{self.savePath}/splineAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Timestamp', 'Skroot Growth Index (SGI)', 'Signal Strength (dB)'])
            writer.writerows(zip(self.time, self.timestamp, self.frequencyToIndex(self.minFrequencySpline), self.minDbSpline))
        with open(f'{self.savePath}/noFitAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Skroot Growth Index (SGI)', 'Signal Strength (dB)'])
            writer.writerows(zip(self.time, self.timestamp, self.minFrequencyRaw, self.minDbRaw))
        with open(f'{self.savePath}/denoisedAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Skroot Growth Index (SGI)'])
            writer.writerows(zip(self.denoiseTime, self.frequencyToIndex(self.denoiseFrequency)))

    def setZeroPoint(self, zeroPoint):
        self.zeroPoint = zeroPoint

    def frequencyToIndex(self, frequencyVector):
        return [-(val - frequencyVector[self.zeroPoint]) for val in frequencyVector]

    def determineFitPoints(self):
        minMag = abs(min(self.scanMagnitude))
        meanMag = abs(mean(self.scanMagnitude))
        if (minMag - meanMag) < 1:
            return self.smallPeakPoints
        elif (minMag - meanMag) > 1:
            return self.largePeakPoints


def denoise(x, y, threshold, points):
    data = np.column_stack([x, y])
    dbsc = DBSCAN(eps=threshold, min_samples=points).fit(StandardScaler().fit(data).transform(data))
    core_samples = np.zeros_like(dbsc.labels_, dtype=bool)
    core_samples[dbsc.core_sample_indices_] = True
    denoiseX = [xval for xval in x if core_samples[x.index(xval)]]
    denoiseY = [y[i] for i in range(len(y)) if core_samples[i]]
    return denoiseX, denoiseY


def findMinSpline(frequency, magnitude):
    try:
        denoisedFrequency, denoisedMagnitude = denoise(frequency, magnitude, 0.2, 3)
        raw_min_index = denoisedMagnitude.index(min(denoisedMagnitude))
        MinFunc = CubicSpline(denoisedFrequency, denoisedMagnitude)
        xrange = np.arange(denoisedFrequency[raw_min_index] - 5, denoisedFrequency[raw_min_index] + 5, 0.001)
        yrange = MinFunc(xrange)
        FuncMin = min(yrange)
        FuncMin_dB = xrange[list(yrange).index(FuncMin)]
        minMag = FuncMin
        minFreq = FuncMin_dB
        return minMag, minFreq
    except:
        logger.exception("Failed to analyze scan")
        return np.nan, np.nan


def getDenoiseParameters(numberOfTimePoints):
    if len(numberOfTimePoints) > 1000:
        return 0.2, 20
    elif len(numberOfTimePoints) > 100:
        return 0.5, 10
    elif len(numberOfTimePoints) > 20:
        return 0.6, 2
    else:
        return 1, 1


def findMinDataSpline(filename):
    frequency, magnitude = extractValuesFromScanFile(filename)
    return findMinSpline(frequency, magnitude)


def extractValuesFromScanFile(filename):
    try:
        # The first few values are known to be inaccurate, and are ignored
        readings = pandas.read_csv(filename)[7:-1]
        return readings['Frequency (MHz)'].values.tolist(), readings['Signal Strength (dB)'].values.tolist()
    except ValueError:
        logger.exception("Rows named improperly")
        return [], []
    except FileNotFoundError:
        logger.exception(f"File does not exist {filename}")
        return [], []
    except:
        logger.exception("Unknown error parsing file")


def findRawMinimum(frequency, magnitude):
    _, denoisedMagnitude = denoise(frequency, magnitude, 0.2, 3)
    rawMinimum = min(denoisedMagnitude)
    minIndeces = [index for index, element in enumerate(denoisedMagnitude) if element == rawMinimum]
    minIndex = int(round(mean(minIndeces), 0))
    rawFreq = frequency[minIndex]
    return minIndex, rawFreq, rawMinimum


def findQuadraticMinimum(frequency, magnitude, rawMinimum, pointsUsed):
    Max = 0.1
    finalMagnitude = []
    while len(finalMagnitude) <= pointsUsed and Max < 4:
        Max += .05
        finalMagnitude = [dB for dB in magnitude if rawMinimum < dB < rawMinimum + Max]
    magnitudeIndeces = [index for index, mag in enumerate(finalMagnitude) if rawMinimum < mag < rawMinimum + Max]
    frequenciesUsed = [frequency[index] for index in magnitudeIndeces]
    with warnings.catch_warnings():
        warnings.filterwarnings('error')
        try:
            quadraticCoefficients = np.polyfit(frequenciesUsed, finalMagnitude, 2)
        except np.RankWarning:
            raise badFit()
    frequencies = np.linspace(frequenciesUsed[0], frequenciesUsed[-1], 1000)
    quadraticFunction = np.polyval(quadraticCoefficients, frequencies)
    minMag = min(quadraticFunction)
    minFrequency = frequencies[list(quadraticFunction).index(minMag)]
    return minMag, minFrequency
