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

        self.denoiseTimeSmooth = previousResultSet.denoiseTimeSmooth + [np.nan]
        self.denoiseTime = previousResultSet.denoiseTime + [np.nan]
        self.denoiseFrequencySmooth = previousResultSet.denoiseFrequencySmooth + [np.nan]
        self.denoiseFrequency = previousResultSet.denoiseFrequency + [np.nan]

    def setTime(self, time: float):
        self.time = time

    def setDenoiseTime(self, time: List[float]):
        self.denoiseTime = time

    def setDenoiseTimeSmooth(self, time: List[float]):
        self.denoiseTimeSmooth = time

    def setDenoiseFrequency(self, frequency: List[float]):
        self.denoiseFrequency = frequency

    def setDenoiseFrequencySmooth(self, frequency: List[float]):
        self.denoiseFrequencySmooth = frequency

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
