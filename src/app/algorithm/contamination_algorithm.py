import logging

import numpy as np

from src.app.algorithm.algorithm_interface import AlgorithmInterface
from src.app.widget.indicator import Indicator


class ContaminationAlgorithm(AlgorithmInterface, Indicator):
    def __init__(self, outerFrame, readerNumber):
        Indicator.__init__(self)
        self.readerNumber = readerNumber
        self.continuousContaminated = 0
        self.backgroundColor = None
        self.contaminated = False
        self.createIndicator(outerFrame)
        self.updateContaminationJson(self.secondaryColor)

    def check(self, resultSet):
        if len(resultSet.getTime()) > 201:
            if not self.contaminated:
                self.contaminated = self.contaminationAlgorithm(
                    resultSet.getTime(),
                    resultSet.getMaxFrequency(),
                    [100, 100],
                )
                if self.contaminated:
                    logging.info(f'Flask {self.readerNumber} is contaminated at time {resultSet.getTime()[-1]} hours')
                    self.updateContaminationJson(self.lightRed)

    def getStatus(self):
        return self.contaminated

    """ End of publicly required algorithms by future interface. """

    def contaminationAlgorithm(self, time, frequency, window):
        time_to_analyze = len(time) - 1
        if not window:
            window = [100, 100]
        coeff_current = np.polyfit(time[time_to_analyze - window[0]:time_to_analyze],
                                   frequency[time_to_analyze - window[0]:time_to_analyze], 1)
        coeff_previous = np.polyfit(time[time_to_analyze - window[0] - window[1]:time_to_analyze - window[0]],
                                    frequency[time_to_analyze - window[0] - window[1]:time_to_analyze - window[0]], 1)
        slopes = [coeff_current[0], coeff_previous[0]]
        if abs(slopes[0]) > abs(slopes[1]) * 10 and abs(slopes[1]) > 0.03:
            self.continuousContaminated += 1
            if self.continuousContaminated > 5:
                return True
            else:
                return False
        else:
            self.continuousContaminated = 0
            return False

    def updateContaminationJson(self, contaminationColor):
        self.backgroundColor = contaminationColor

