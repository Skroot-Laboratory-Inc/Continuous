from typing import List

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

    def setTime(self, time: float):
        self.time = time

    def setMaxFrequency(self, maxFrequency: float):
        self.maxFrequency = maxFrequency

    def setMaxVoltsSmooth(self, maxVolts: float):
        self.maxVoltsSmooth = maxVolts

    def setMaxFrequencySmooth(self, maxFrequencySmoothed: float):
        self.maxFrequencySmooth = maxFrequencySmoothed

    def setPeakWidthSmooth(self, peakWidthSmooth: float):
        self.peakWidthSmooth = peakWidthSmooth

    def setFilename(self, filename: str):
        self.filename = filename

    def setTimestamp(self, timestamp: int):
        self.timestamp = timestamp

    def setDerivative(self, derivative: float):
        self.derivative = derivative
