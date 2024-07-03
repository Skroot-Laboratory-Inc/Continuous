import csv
import logging

import numpy as np
from scipy.signal import savgol_filter

from src.app.algorithm.algorithm_interface import AlgorithmInterface
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.properties.harvest_properties import HarvestProperties
from src.app.widget.indicator import Indicator


class HarvestAlgorithm(AlgorithmInterface):
    def __init__(self, fileManager: ReaderFileManager, experimentNotes, readerNumber, indicator: Indicator):
        self.experimentNotes = experimentNotes
        self.readerNumber = readerNumber
        self.Indicator = indicator
        harvestProperties = HarvestProperties()
        self.hoursAfterInoculation = harvestProperties.hoursAfterInoculation
        self.closeToHarvestThreshold = harvestProperties.closeToHarvestThreshold
        self.consecutivePoints = harvestProperties.consecutivePoints
        self.savgolPoints = harvestProperties.savgolPoints
        self.backwardPoints = harvestProperties.backwardPoints
        self.FileManager = fileManager
        self.inoculated = False
        self.indicatorColor = None
        self.closeToHarvest = False
        self.readyToHarvest = False
        self.harvested = False
        self.inoculatedTime = 0
        self.continuousHarvest = 0
        self.continuousHarvestReady = 0

    def check(self, resultSet):
        if self.inoculated:
            if resultSet.getTime()[-1] > (self.inoculatedTime + self.hoursAfterInoculation):
                if not self.readyToHarvest:
                    self.harvestAlgorithm(resultSet.getDenoiseTime(), resultSet.getDenoiseFrequency())

    def getStatus(self):
        return self.harvested

    """ End of publicly visible functions required for algorithms. """

    def harvestAlgorithm(self, time, frequency):
        ysmooth = savgol_filter(frequency, self.savgolPoints, 2)
        dydxSmooth = np.diff(ysmooth, 1)
        smoothedSlopes = []
        for i in range(self.savgolPoints, len(dydxSmooth[:-self.backwardPoints])):
            smoothedSlopes.append(np.polyfit(time[i - self.savgolPoints:i], dydxSmooth[i - self.savgolPoints:i], 1)[0])
        with open(self.FileManager.getAccelerationCsv(), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Acceleration'])
            writer.writerows(zip(time[self.savgolPoints:-self.backwardPoints], smoothedSlopes))
        if smoothedSlopes[-1] < -self.closeToHarvestThreshold or smoothedSlopes[-1] > self.closeToHarvestThreshold:
            lastFiveIncreasing = all(i < j for i, j in zip(smoothedSlopes[-self.consecutivePoints:], smoothedSlopes[
                                                                                                     -self.consecutivePoints + 1:]))  # Checks that the list of 5 is strictly increasing
            previousFiveDecreasing = all(i > j for i, j in
                                         zip(smoothedSlopes[-self.consecutivePoints * 2:-self.consecutivePoints],
                                             smoothedSlopes[
                                             -self.consecutivePoints * 2 + 1:-self.consecutivePoints]))  # Checks that the list of 5 is strictly decreasing
            lastFiveDecreasing = all(i > j for i, j in zip(smoothedSlopes[-self.consecutivePoints:], smoothedSlopes[
                                                                                                     -self.consecutivePoints + 1:]))  # Checks that the list of 5 is strictly decreasing
            previousFiveIncreasing = all(i < j for i, j in
                                         zip(smoothedSlopes[-self.consecutivePoints * 2:-self.consecutivePoints],
                                             smoothedSlopes[
                                             -self.consecutivePoints * 2 + 1:-self.consecutivePoints]))  # Checks that the list of 5 is strictly increasing
            if not self.closeToHarvest:
                if lastFiveIncreasing and previousFiveDecreasing:
                    logging.info(
                        f'Flask {self.readerNumber} is close to harvest at time {time[-1]} hours for {time[-self.backwardPoints]}')
                    self.Indicator.changeIndicatorYellow()
                    self.closeToHarvest = True
            else:
                if lastFiveDecreasing and previousFiveIncreasing:
                    logging.info(
                        f'Flask {self.readerNumber} is ready to harvest at time {time[-1]} hours for {time[-self.backwardPoints]}')
                    self.Indicator.changeIndicatorRed()
                    self.readyToHarvest = True

    def updateInoculation(self, analyzer):
        self.inoculated = True
        self.inoculatedTime = analyzer.getTime()[-1]
        self.experimentNotes.updateExperimentNotes('Inoculated')
        logging.info(f'Flask {self.readerNumber} is inoculated at time {self.inoculatedTime}')
