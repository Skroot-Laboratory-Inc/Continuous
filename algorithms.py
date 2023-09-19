import csv
import threading
import tkinter as tk

import numpy as np
from scipy.signal import savgol_filter

import logger
import text_notification
from analysis import Analysis
from dac import Dac
from indicator import Indicator
from notes import ExperimentNotes


class HarvestAlgorithm(Indicator, ExperimentNotes):
    def __init__(self, outerFrame, AppModule, Emailer):
        Indicator.__init__(self)
        self.Emailer = Emailer
        self.AppModule = AppModule
        self.inoculated = False
        self.indicatorColor = None
        self.closeToHarvest = False
        self.readyToHarvest = False
        self.inoculatedTime = 0
        self.hoursAfterInoculation = 2
        self.closeToHarvestThreshold = 0.005
        self.consecutivePoints = 8
        self.savgolPoints = 51
        self.backwardPoints = 25
        self.harvested = False
        self.continuousHarvest = 0
        self.continuousHarvestReady = 0
        self.createIndicator(outerFrame)

    def addInoculationMenuBar(self, menu):
        menu.add_command(label=f"Reader {self.readerNumber} Inoculated", command=lambda: self.updateInoculation())

    def updateInoculation(self):
        self.inoculated = True
        self.inoculatedTime = self.time[-1]
        for Reader in self.AppModule.Readers:
            Reader.setZeroPoint(len(self.time)-1)
        self.updateExperimentNotes('Inoculated')
        logger.info(f'Flask {self.readerNumber} is inoculated at time {self.time[-1]}')

    def checkHarvest(self):
        if self.inoculated:
            if self.time[-1] > (self.inoculatedTime + self.hoursAfterInoculation):
                if not self.readyToHarvest:
                    self.harvestAlgorithm(self.denoiseTime, self.denoiseFrequency)

    def harvestAlgorithm(self, time, frequency):
        ysmooth = savgol_filter(frequency, self.savgolPoints, 2)
        dydxSmooth = np.diff(ysmooth, 1)
        smoothedSlopes = []
        for i in range(self.savgolPoints, len(dydxSmooth[:-self.backwardPoints])):
            smoothedSlopes.append(np.polyfit(time[i - self.savgolPoints:i], dydxSmooth[i - self.savgolPoints:i], 1)[0])
        with open(f'{self.savePath}/Acceleration.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (hours)', 'Acceleration'])
            writer.writerows(zip(self.time[self.savgolPoints:-self.backwardPoints], smoothedSlopes))
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
                    logger.info(
                        f'Flask {self.readerNumber} is close to harvest at time {self.time[-1]} hours for {self.time[-self.backwardPoints]}')
                    if self.AppModule.emailSetting:
                        self.Emailer.sendMessage()
                        self.Emailer.setMessageHarvestReady()
                    self.changeIndicatorYellow()
                    self.closeToHarvest = True
            else:
                if lastFiveDecreasing and previousFiveIncreasing:
                    logger.info(
                        f'Flask {self.readerNumber} is ready to harvest at time {self.time[-1]} hours for {self.time[-self.backwardPoints]}')
                    if self.AppModule.emailSetting:
                        self.Emailer.sendMessage()
                    self.changeIndicatorRed()
                    self.readyToHarvest = True


class ContaminationAlgorithm(Analysis, Indicator):
    def __init__(self, outerFrame, AppModule, Emailer, readerNumber):
        Indicator.__init__(self)
        self.readerNumber = readerNumber
        self.AppModule = AppModule
        self.continuousContaminated = 0
        self.backgroundColor = None
        self.contaminated = False
        self.createIndicator(outerFrame)
        self.updateContaminationJson(self.white)
        self.Emailer = Emailer

    def checkContamination(self):
        if len(self.time) > 201 and self.AppModule.cellApp is True:
            if not self.contaminated:
                self.contaminated = self.contaminationAlgorithm(self.time, self.minFrequency, [100, 100])
                if self.contaminated:
                    logger.info(f'Flask {self.readerNumber} is contaminated at time {self.time[-1]} hours')
                    self.updateContaminationJson(self.lightRed)

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


class FoamingAlgorithm(Analysis):
    def __init__(self, airFreq, waterFreq, waterShift, AppModule, Emailer):
        self.AppModule = AppModule
        self.Emailer = Emailer
        self.referenceFrequency = None
        self.foamThresh = 10
        self.scanRate = 0.1
        self.startFreq = airFreq - 15
        self.stopFreq = airFreq + 15
        self.nPoints = 350
        self.airFreq = airFreq
        self.waterFreq = waterFreq
        self.waterShift = waterShift
        self.errorThread = ''
        self.liquidThread = ''
        self.Dac = Dac()

    def checkFoaming(self):
        if self.airFreq != 0:
            self.referenceFrequency = self.minFrequency[0]
            shift = abs(self.minFrequency[-1] - self.referenceFrequency)
            logger.info(f'shift: {shift}, needed shift {self.waterShift * (self.foamThresh / 100)}')
            if shift > (self.waterShift * 0.9) and self.errorThread == '' and self.liquidThread == '':
                self.liquidThread = threading.Thread(target=self.liquidReachedSensor, args=())
                self.liquidThread.start()
            elif shift > self.waterShift * (
                    self.foamThresh / 100) and self.errorThread == '' and self.liquidThread == '':
                self.errorThread = threading.Thread(target=self.foamReachedSensor, args=())
                self.errorThread.start()
            else:
                try:
                    self.Dac.send_ma(4)
                except:
                    logger.exception("Failed to initialize DAC")
        else:
            pass

    def liquidReachedSensor(self):
        text_notification.setText("LIQUID \nOVERFLOW", ('Courier', 9, 'bold'), self.AppModule.royalBlue, 'red')
        tk.messagebox.showwarning(f'LIQUID OVERFLOW', "LIQUID OVERFLOW!")
        self.liquidThread = ''
        return

    def foamReachedSensor(self):
        text_notification.setText(f"Foam reached sensor", ('Courier', 12, 'bold'), self.AppModule.royalBlue,
                                  self.AppModule.white)
        try:
            self.Dac.send_ma(20)
        except:
            logger.exception("Failed to initialize DAC")
        tk.messagebox.showinfo(f'Foaming notification', f"Foam has reached sensor")
        self.errorThread = ''
        return
