import datetime
import logging

import numpy as np
from scipy.optimize import curve_fit

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.data_helpers import gaussian
from src.app.helper_methods.datetime_helpers import datetimeToMillis, millisToDatetime
from src.app.properties.harvest_properties import HarvestProperties
from src.app.reader.algorithm.algorithm_interface import AlgorithmInterface


class HarvestAlgorithm(AlgorithmInterface):
    def __init__(self, fileManager: ReaderFileManager):
        self.derivativePoints = HarvestProperties().derivativePoints
        self.FileManager = fileManager
        self.readyToHarvest = False
        self.harvested = False
        self.historicalHarvestTime = []
        self.currentHarvestPrediction = np.nan
        self.differentPredictions = []

    def check(self, resultSet):
        center, std, rSquared, harvestTime = np.nan, np.nan, np.nan, np.nan
        if len(resultSet.getTime()) > self.derivativePoints:
            center, std, rSquared, harvestTime = self.harvestAlgorithm(resultSet.getTimestamps(), resultSet.getTime(), resultSet.getDerivativeMean())
        self.historicalHarvestTime.append(harvestTime)
        return harvestTime

    def getStatus(self):
        return self.harvested

    """ End of publicly visible functions required for algorithms. """

    def harvestAlgorithm(self, timestamps, time, derivative):
        centroid, std, rSquared = self.findGaussianStd(time, derivative)
        if len(time) != len(derivative):
            logging.warning(
                f"Cannot estimate harvest window, len(time)={len(time)} != len(derivative)={len(derivative)}",
                extra={"id": "harvest algorithm"},
            )
        proposedHarvestTime = centroid + HarvestProperties().standardDeviationsToHarvest * std
        if self.harvestTrackable(centroid, rSquared, time[-1], derivative[-1], proposedHarvestTime):
            self.differentPredictions.append(datetimeToMillis(timestamps[0] + datetime.timedelta(hours=(proposedHarvestTime - time[0]))))
            if len(self.differentPredictions) > 20:
                self.currentHarvestPrediction = round(np.nanmean(self.differentPredictions[-20:]))
            else:
                self.currentHarvestPrediction = round(np.nanmean(self.differentPredictions))
        harvestTime = self.currentHarvestPrediction
        return centroid, std, rSquared, harvestTime

    def harvestTrackable(self, centroid, rSquared, currentTime, currentDerivative, proposedHarvestTime) -> bool:
        trackable = False
        if self.isStableGaussian(rSquared) and self.isPastPeak(currentTime, centroid) and self.isReasonableTime(currentTime, currentDerivative, proposedHarvestTime):
            trackable = True
        return trackable

    def isPastPeak(self, x, y):
        return self.distanceFromYEqualsX(x, y) > HarvestProperties().distanceFromYEqualsX

    @staticmethod
    def isReasonableTime(timePoint, derivativePoint, proposedHarvestTime):
        isAtLeastXHoursOut = timePoint + HarvestProperties().hoursFromHarvest < proposedHarvestTime
        isLessThanXHoursOut = proposedHarvestTime < timePoint + HarvestProperties().hoursToHarvestEstimate
        isFastGrowth = derivativePoint > HarvestProperties().fastDerivativeThreshold
        isInInitialGrowth = timePoint > HarvestProperties().daysNotToEstimateHarvest * 24
        return isAtLeastXHoursOut and isLessThanXHoursOut and (isFastGrowth or isInInitialGrowth)

    @staticmethod
    def isStableGaussian(rSquared):
        return rSquared > HarvestProperties().rSquaredThreshold

    @staticmethod
    def distanceFromYEqualsX(x, y):
        return abs(x - y) / (2 ** 0.5)

    @staticmethod
    def findGaussianStd(x, y):
        try:
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
            indeces = [index for index, xVal in enumerate(x) if centroid + std/2 > xVal > centroid - std/2]
            yNearPeak = [y[ind] for ind in indeces]
            xNearPeak = [x[ind] for ind in indeces]
            if xNearPeak and yNearPeak != []:
                popt, _ = curve_fit(
                    gaussian,
                    xNearPeak,
                    yNearPeak,
                    p0=(np.nanmax(yNearPeak), xNearPeak[np.nanargmax(yNearPeak)], 1),
                    bounds=([np.nanmin(yNearPeak), np.nanmin(xNearPeak), 0], [np.inf, np.nanmax(xNearPeak), np.inf]),
                    nan_policy="omit"
                )
                amplitude = popt[0]
                centroid = popt[1]
                std = popt[2]
                residuals = np.array(yNearPeak) - np.array(gaussian(xNearPeak, *popt))
                ss_res = np.nansum(residuals ** 2)
                ss_tot = np.nansum((yNearPeak - np.nanmean(yNearPeak)) ** 2)
                rSquared = 1 - (ss_res / ss_tot)
                return centroid, std, rSquared
            else:
                return np.nan, np.nan, np.nan
        except:
            return np.nan, np.nan, np.nan

