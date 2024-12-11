from datetime import datetime
from typing import List

import numpy as np
from scipy.signal import savgol_filter

from src.app.helper.helper_functions import frequencyToIndex
from src.app.model.result_set.result_set_data_point import ResultSetDataPoint


class ResultSet:
    def __init__(self):
        self.time = []
        self.maxFrequency = []
        self.maxVoltsSmooth = []
        self.maxFrequencySmooth = []
        self.filenames = []
        self.timestamps = []
        self.peakWidthsSmooth = []
        self.derivative = []
        self.secondDerivative = []
        self.cubic = []

        self.denoiseTimeSmooth = []
        self.denoiseTime = []
        self.denoiseFrequencySmooth = []
        self.denoiseFrequency = []

    def getTime(self) -> List[float]:
        return self.time

    def getPeakWidthsSmooth(self) -> List[float]:
        return self.peakWidthsSmooth

    def getMaxFrequency(self) -> List[float]:
        return self.maxFrequency

    def getMaxVoltsSmooth(self) -> List[float]:
        return self.maxVoltsSmooth

    def getMaxFrequencySmooth(self) -> List[float]:
        return self.maxFrequencySmooth

    def getFilenames(self) -> List[str]:
        return self.filenames

    def getDerivative(self) -> List[float]:
        return self.derivative

    def getSecondDerivative(self) -> List[float]:
        return self.secondDerivative

    def getCubic(self) -> List[float]:
        return self.cubic

    def getTimestamps(self) -> List[datetime]:
        return self.timestamps

    def getDenoiseTime(self) -> List[float]:
        return self.denoiseTime

    def getDenoiseTimeSmooth(self) -> List[float]:
        return self.denoiseTimeSmooth

    def getDenoiseFrequency(self) -> List[float]:
        return self.denoiseFrequency

    def getDenoiseFrequencySmooth(self) -> List[float]:
        return self.denoiseFrequencySmooth

    def resetRun(self):
        self.time = self.time[-1:]
        self.maxVoltsSmooth = self.maxVoltsSmooth[-1:]
        self.maxFrequency = self.maxFrequency[-1:]
        self.maxFrequencySmooth = self.maxFrequencySmooth[-1:]
        self.filenames = self.filenames[-1:]
        self.timestamps = self.timestamps[-1:]
        self.peakWidthsSmooth = self.peakWidthsSmooth[-1:]
        self.cubic = self.cubic[-1:]
        self.derivative = self.derivative[-1:]
        self.secondDerivative = self.secondDerivative[-1:]

        self.denoiseFrequency = self.denoiseFrequency[-1:]
        self.denoiseFrequencySmooth = self.denoiseFrequencySmooth[-1:]
        self.denoiseTime = self.denoiseTime[-1:]
        self.denoiseTimeSmooth = self.denoiseTimeSmooth[-1:]

    def setValues(self, values: ResultSetDataPoint):
        self.time.append(values.time)
        self.maxFrequency.append(values.maxFrequency)
        self.maxVoltsSmooth.append(values.maxVoltsSmooth)
        self.maxFrequencySmooth.append(values.maxFrequencySmooth)
        self.filenames.append(values.filename)
        self.timestamps.append(values.timestamp)
        self.peakWidthsSmooth.append(values.peakWidthSmooth)
        self.cubic.append(values.cubic)
        self.derivative.append(values.derivative)
        self.secondDerivative.append(values.secondDerivative)

        # Denoise values change with time, so the entire array gets set at once.
        self.denoiseTime = values.denoiseTime
        self.denoiseTimeSmooth = values.denoiseTimeSmooth
        self.denoiseFrequency = values.denoiseFrequency
        self.denoiseFrequencySmooth = values.denoiseFrequencySmooth

