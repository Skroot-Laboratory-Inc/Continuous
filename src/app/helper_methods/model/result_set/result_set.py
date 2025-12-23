from datetime import datetime
from typing import List

import numpy as np
from scipy.signal import savgol_filter

from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.helper_methods.model.result_set.result_set_data_point import ResultSetDataPoint
from src.app.properties.harvest_properties import HarvestProperties


class ResultSet:
    def __init__(self):
        self.startTime = datetimeToMillis(datetime.now())
        self.time = []
        self.maxFrequency = []
        self.maxVoltsSmooth = []
        self.maxFrequencySmooth = []
        self.filenames = []
        self.timestamps = []
        self.peakWidthsSmooth = []
        self.derivative = []
        self.derivativeMean = []
        self.smoothDerivativeMean = []

        # Store indices of denoised data instead of separate arrays
        self.denoiseIndices = []
        self.denoiseSmoothIndices = []

    def getStartTime(self) -> int:
        return self.startTime

    def getTime(self) -> List[float]:
        return self.time

    def getPeakWidthsSmooth(self) -> List[float]:
        return self.peakWidthsSmooth

    def getMaxFrequency(self) -> List[float]:
        return self.maxFrequency

    def getMaxVoltsSmooth(self) -> List[float]:
        return self.maxVoltsSmooth

    def getCurrentVolts(self) -> float:
        if len(self.maxVoltsSmooth) > 0:
            return self.maxVoltsSmooth[-1]
        else:
            return np.nan

    def getMaxFrequencySmooth(self) -> List[float]:
        return self.maxFrequencySmooth

    def getCurrentFrequency(self) -> float:
        if len(self.maxFrequencySmooth) > 0:
            return self.maxFrequencySmooth[-1]
        else:
            return np.nan

    def getFilenames(self) -> List[str]:
        return self.filenames

    def getDerivativeMean(self) -> List[float]:
        return self.smoothDerivativeMean

    def getTimestamps(self) -> List[int]:
        return self.timestamps

    def getDenoiseTime(self) -> List[float]:
        """Get denoised time values by filtering the time array using denoiseIndices"""
        return [self.time[i] for i in self.denoiseIndices if i < len(self.time)]

    def getDenoiseTimeSmooth(self) -> List[float]:
        """Get denoised smooth time values by filtering the time array using denoiseSmoothIndices"""
        return [self.time[i] for i in self.denoiseSmoothIndices if i < len(self.time)]

    def getDenoiseFrequency(self) -> List[float]:
        """Get denoised frequency values by filtering the maxFrequency array using denoiseIndices"""
        return [self.maxFrequency[i] for i in self.denoiseIndices if i < len(self.maxFrequency)]

    def getDenoiseFrequencySmooth(self) -> List[float]:
        """Get denoised smooth frequency values by filtering the maxFrequencySmooth array using denoiseSmoothIndices"""
        return [self.maxFrequencySmooth[i] for i in self.denoiseSmoothIndices if i < len(self.maxFrequencySmooth)]

    def getDenoiseFilenames(self) -> List[str]:
        """Get filenames corresponding to denoised data points"""
        return [self.filenames[i] for i in self.denoiseIndices if i < len(self.filenames)]

    def getDenoiseTimestamps(self) -> List[int]:
        """Get timestamps corresponding to denoised data points"""
        return [self.timestamps[i] for i in self.denoiseIndices if i < len(self.timestamps)]

    def getDenoiseSmoothTimestamps(self) -> List[int]:
        """Get timestamps corresponding to denoised smooth data points"""
        return [self.timestamps[i] for i in self.denoiseSmoothIndices if i < len(self.timestamps)]

    def resetRun(self):
        self.time = self.time[-1:]
        self.maxVoltsSmooth = self.maxVoltsSmooth[-1:]
        self.maxFrequency = self.maxFrequency[-1:]
        self.maxFrequencySmooth = self.maxFrequencySmooth[-1:]
        self.filenames = self.filenames[-1:]
        self.timestamps = self.timestamps[-1:]
        self.peakWidthsSmooth = self.peakWidthsSmooth[-1:]
        self.derivative = self.derivative[-1:]
        self.derivativeMean = self.derivativeMean[-1:]
        self.smoothDerivativeMean = self.derivativeMean[-1:]

        # Reset indices - keep only index 0 if it exists
        self.denoiseIndices = [0] if 0 in self.denoiseIndices else []
        self.denoiseSmoothIndices = [0] if 0 in self.denoiseSmoothIndices else []

    def setValues(self, values: ResultSetDataPoint):
        self.time.append(values.time)
        self.maxFrequency.append(values.maxFrequency)
        self.maxVoltsSmooth.append(values.maxVoltsSmooth)
        self.maxFrequencySmooth.append(values.maxFrequencySmooth)
        self.filenames.append(values.filename)
        self.timestamps.append(values.timestamp)
        self.peakWidthsSmooth.append(values.peakWidthSmooth)
        self.derivative.append(values.derivative)
        if len(self.derivative) > HarvestProperties().derivativePoints:
            self.derivativeMean.append(self.takeDerivativeMean(self.derivative))
            if len(self.derivativeMean) > 151:
                self.smoothDerivativeMean = savgol_filter(self.derivativeMean, 151, 2)
            else:
                self.smoothDerivativeMean = self.derivativeMean
        else:
            self.derivativeMean.append(np.nan)
            self.smoothDerivativeMean.append(np.nan)

        # Denoise indices change with time, so the entire list gets set at once.
        self.denoiseIndices = values.denoiseIndices
        self.denoiseSmoothIndices = values.denoiseSmoothIndices

    @staticmethod
    def takeDerivativeMean(rawValues: List[float]):
        return np.nanmean(rawValues[-HarvestProperties().derivativePoints:])

