import numpy as np


class ResultSetDataPoint:
    def __init__(self, previousResultSet):
        self.time = np.nan
        self.maxFrequency = np.nan
        self.maxVoltsSmooth = np.nan
        self.maxFrequencySmooth = np.nan
        self.filename = ""
        self.timestamp = np.nan
        self.peakWidthSmooth = np.nan
        self.derivative = np.nan

        self.denoiseTimeSmooth = previousResultSet.denoiseTimeSmooth + [np.nan]
        self.denoiseTime = previousResultSet.denoiseTime + [np.nan]
        self.denoiseFrequencySmooth = previousResultSet.denoiseFrequencySmooth + [np.nan]
        self.denoiseFrequency = previousResultSet.denoiseFrequency + [np.nan]

    def setTime(self, time):
        self.time = time

    def setDenoiseTime(self, time):
        self.denoiseTime = time

    def setDenoiseTimeSmooth(self, time):
        self.denoiseTimeSmooth = time

    def setDenoiseFrequency(self, frequency):
        self.denoiseFrequency = frequency

    def setDenoiseFrequencySmooth(self, frequency):
        self.denoiseFrequencySmooth = frequency

    def setMaxFrequency(self, maxFrequency):
        self.maxFrequency = maxFrequency

    def setMaxVoltsSmooth(self, maxVolts):
        self.maxVoltsSmooth = maxVolts

    def setMaxFrequencySmooth(self, maxFrequencySmoothed):
        self.maxFrequencySmooth = maxFrequencySmoothed

    def setPeakWidthSmooth(self, peakWidthSmooth):
        self.peakWidthSmooth = peakWidthSmooth

    def setFilename(self, filename):
        self.filename = filename

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp

    def setDerivative(self, derivative):
        self.derivative = derivative
