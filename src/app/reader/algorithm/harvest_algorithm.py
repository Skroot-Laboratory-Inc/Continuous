import csv
import logging

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

from src.app.helper.helper_functions import gaussian
from src.app.model.result_set.result_set import ResultSet
from src.app.reader.algorithm.algorithm_interface import AlgorithmInterface
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.properties.harvest_properties import HarvestProperties
from src.app.reader.analyzer.analyzer import Analyzer
from src.app.widget import text_notification
from src.app.widget.indicator import Indicator


class HarvestAlgorithm(AlgorithmInterface):
    def __init__(self, fileManager: ReaderFileManager):
        self.derivativePoints = HarvestProperties().derivativePoints
        self.savgolPoints = HarvestProperties().savgolPoints
        self.FileManager = fileManager
        self.readyToHarvest = False
        self.harvested = False

    def check(self, resultSet):
        if len(resultSet.getDenoiseTime()) > self.savgolPoints:
            self.harvestAlgorithm(resultSet.getDenoiseTime(), resultSet.getDerivative())

    def getStatus(self):
        return self.harvested

    """ End of publicly visible functions required for algorithms. """

    def harvestAlgorithm(self, time, derivative):
        smoothedDerivative = savgol_filter(derivative, self.savgolPoints, 2)
        centroid, std = self.findGaussianStd(time, smoothedDerivative)
        logging.info(f"Found std={std}", extra={"id": "std"})
        print(f"{centroid}, {std}")
        return centroid, std

    @staticmethod
    def findGaussianStd(x, y):
        popt, _ = curve_fit(
            gaussian,
            x,
            y,
            p0=(np.nanmax(y), x[np.nanargmax(y)], 1),
            bounds=([np.nanmin(y), np.nanmin(x), 0], [np.inf, np.nanmax(x), np.inf]),
            nan_policy="omit"
        )
        amplitude = popt[0]
        centroid = popt[1]
        std = popt[2]
        return centroid, std

