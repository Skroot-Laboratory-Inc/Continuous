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
        self.denoiseFrequencySmooth = []
        self.denoiseTimeSmooth = []
        self.denoiseTotalMinSmooth = []
        self.denoiseTimeDbSmooth = []
        self.denoisePoints = 1
        self.denoiseRadius = 1
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
        try:
            minMag, minFreq, rawMinMag, rawMinFreq = self.findMinData(filename)
            self.minDb.append(minMag)
            self.minFrequency.append(minFreq)
            self.minDbRaw.append(minMag)
            self.minFrequencyRaw.append(minFreq)
        except:
            logger.exception("Failed to analyze scan normally")
            self.minDb.append(0)
            self.minFrequency.append(0)
            self.minDbRaw.append(0)
            self.minFrequencyRaw.append(0)
        try:
            minMag, minFreq, rawMinMag, rawMinFreq = self.findMinDataSmooth(filename)
            self.minDbSmooth.append(minMag)
            self.minFrequencySmooth.append(minFreq)
        except:
            logger.exception("Failed to analyze smoothed scan")
            self.minDbSmooth.append(0)
            self.minFrequencySmooth.append(0)
        try:
            minMag, minFreq = self.findMinDataSpline(filename)
            self.minDbSpline.append(minMag)
            self.minFrequencySpline.append(minFreq)
        except:
            logger.exception("Failed to analyze spline scan")
            self.minDbSpline.append(0)
            self.minFrequencySpline.append(0)
        self.time.append((self.scanNumber - 100000) / 60)
        self.timestamp.append(datetime.now())

    def findMinData(self, filename):
        try:
            readings1 = pandas.read_csv(filename)
            readings = readings1[7:-1]
            frequency = readings['Frequency (MHz)'].values.tolist()
            dB = readings['Signal Strength (dB)'].values.tolist()
            self.scanFrequency, self.scanMagnitude = frequency, dB
            return self.findMin(frequency, dB)
        except:
            logger.exception("Failed to get data from file")
        return 0, 0, 0, 0

    def findMinDataSmooth(self, filename):
        try:
            readings1 = pandas.read_csv(filename)
            readings = readings1[7:-1]
            frequency = readings['Frequency (MHz)'].values.tolist()
            dB = readings['Signal Strength (dB)'].values.tolist()
            dBSmooth = savgol_filter(dB, 501, 2)
            self.scanFrequency, self.scanMagnitude = frequency, dBSmooth
            return self.findMin(frequency, dBSmooth)
        except:
            logger.exception("Failed to get data from file")
        return 0, 0, 0, 0

    def findMin(self, frequency, dB):
        try:
            data = np.column_stack([frequency, dB])
            stscaler = StandardScaler().fit(data)
            data = stscaler.transform(data)
            dbsc = DBSCAN(eps=0.20, min_samples=3).fit(data)
            labels = dbsc.labels_
            core_samples = np.zeros_like(labels, dtype=bool)
            core_samples[dbsc.core_sample_indices_] = True
            NewdB = [dB[i] for i in range(len(dB)) if i in dbsc.core_sample_indices_]
            NewFreq = [Freqnew for Freqnew in frequency if frequency.index(Freqnew) in dbsc.core_sample_indices_]
            MindB = min(NewdB)
            MinIndeces = [index for index, element in enumerate(NewdB) if element == MindB]
            minIndex = int(round(mean(MinIndeces), 0))
            FinaldB = []
            Max = 0.1
            pointsUsed = self.determineFitPoints()
            NewMinfrequency = frequency[minIndex - pointsUsed:minIndex + pointsUsed]
            NewMindB = dB[minIndex - pointsUsed:minIndex + pointsUsed]
            while len(FinaldB) <= pointsUsed and Max < 4:
                Max += .05
                FinaldB = [dB for dB in NewMindB if dB < MindB + Max and dB > MindB]
            FinaldBIndeces = [index for index, element in enumerate(NewMindB) if
                              element < MindB + Max and element > MindB]
            FinalFreq = [NewMinfrequency[index] for index in FinaldBIndeces]
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    Mincoeff = np.polyfit(FinalFreq, FinaldB, 2)
                except np.RankWarning:
                    raise badFit()
            Nums = np.linspace(FinalFreq[0], FinalFreq[-1], 1000)
            Minfunc = np.polyval(Mincoeff, Nums)
            FuncMin = min(Minfunc)
            Minfunclist = list(Minfunc)
            FuncMin_dB = Nums[Minfunclist.index(FuncMin)]
            minMag = FuncMin
            minFreq = FuncMin_dB
            rawMag = dB[minIndex]
            rawFreq = frequency[minIndex]
            return minMag, minFreq, rawMag, rawFreq
        except:
            logger.exception("Failed to analyze scan")
        return 0, 0, 0, 0

    def findMinDataSpline(self, filename):
        try:
            readings1 = pandas.read_csv(filename)
            readings = readings1[7:-1]
            frequency = readings['Frequency (MHz)'].values.tolist()
            dB = readings['Signal Strength (dB)'].values.tolist()
            return findMinSpline(frequency, dB)
        except:
            logger.exception("Failed to get data from file")
        return 0, 0, 0, 0

    def denoiseResults(self):
        if len(self.time) > 1000:
            self.denoiseRadius, self.denoisePoints = 0.2, 20
        elif len(self.time) > 100:
            self.denoiseRadius, self.denoisePoints = 0.5, 10
        elif len(self.time) > 20:
            self.denoiseRadius, self.denoisePoints = 0.6, 2
        else:
            self.denoiseRadius, self.denoisePoints = 1, 1
        self.denoiseTime, self.denoiseFrequency = denoise(self.time, self.minFrequency, self.denoiseRadius,
                                                          self.denoisePoints)
        self.denoiseTimeSmooth, self.denoiseFrequencySmooth = denoise(self.time, self.minFrequencySmooth,
                                                                      self.denoiseRadius, self.denoisePoints)
        self.denoiseTimeDb, self.denoiseTotalMin = denoise(self.time, self.minDb, self.denoiseRadius,
                                                           self.denoisePoints)
        self.denoiseTimeDbSmooth, self.denoiseTotalMinSmooth = denoise(self.time, self.minDbSmooth,
                                                                       self.denoiseRadius, self.denoisePoints)

    def createAnalyzedFiles(self):
        with open(f'{self.savePath}/Analyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Timestamp', 'Frequency (MHz)', 'Signal Strength (dB)'])
            writer.writerows(zip(self.time, self.timestamp, self.minFrequency, self.minDb))
        with open(f'{self.savePath}/smoothAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Timestamp', 'Frequency (MHz)', 'Signal Strength (dB)'])
            writer.writerows(zip(self.time, self.timestamp, self.minFrequencySmooth, self.minDbSmooth))
        with open(f'{self.savePath}/splineAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Timestamp', 'Frequency (MHz)', 'Signal Strength (dB)'])
            writer.writerows(zip(self.time, self.timestamp, self.minFrequencySpline, self.minDbSpline))
        with open(f'{self.savePath}/noFitAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Frequency (MHz)', 'Signal Strength (dB)'])
            writer.writerows(zip(self.time, self.timestamp, self.minFrequencyRaw, self.minDbRaw))
        with open(f'{self.savePath}/denoisedAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Frequency (MHz)'])
            writer.writerows(zip(self.denoiseTime, self.denoiseFrequency))

    def determineFitPoints(self):
        minMag = abs(min(self.scanMagnitude))
        meanMag = abs(mean(self.scanMagnitude))
        if (minMag - meanMag) < 1:
            return self.smallPeakPoints
        elif (minMag - meanMag) > 1:
            return self.largePeakPoints


def denoise(x1, FuncMin_dB, Threshold, points):
    InitialLength = len(FuncMin_dB)
    data = np.column_stack([x1, FuncMin_dB])
    stscaler = StandardScaler().fit(data)
    data = stscaler.transform(data)
    dbsc = DBSCAN(eps=Threshold, min_samples=points).fit(data)
    labels = dbsc.labels_
    core_samples = np.zeros_like(labels, dtype=bool)
    core_samples[dbsc.core_sample_indices_] = True
    x1 = [x for x in x1 if core_samples[x1.index(x)] == True]
    FuncMin_dB = [FuncMin_dB[i] for i in range(len(FuncMin_dB)) if core_samples[i] == True]
    FinalLength = len(FuncMin_dB)
    return x1, FuncMin_dB

def findMinSpline(frequency, dB):
    try:
        data = np.column_stack([frequency, dB])
        stscaler = StandardScaler().fit(data)
        data = stscaler.transform(data)
        dbsc = DBSCAN(eps=0.20, min_samples=3).fit(data)
        labels = dbsc.labels_
        core_samples = np.zeros_like(labels, dtype=bool)
        core_samples[dbsc.core_sample_indices_] = True
        NewdB = [dB[i] for i in range(len(dB)) if i in dbsc.core_sample_indices_]
        NewFreq = [Freqnew for Freqnew in frequency if frequency.index(Freqnew) in dbsc.core_sample_indices_]
        raw_min_index = NewdB.index(min(NewdB))
        MinFunc = CubicSpline(NewFreq, NewdB)
        xrange = np.arange(NewFreq[raw_min_index] - 5, NewFreq[raw_min_index] + 5, 0.001)
        yrange = MinFunc(xrange)
        FuncMin = min(yrange)
        FuncMin_dB = xrange[list(yrange).index(FuncMin)]
        minMag = FuncMin
        minFreq = FuncMin_dB
        return minMag, minFreq
    except:
        logger.exception("Failed to analyze scan")
    return 0, 0
