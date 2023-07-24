import os
import shutil
import subprocess as sp
import time
import tkinter as tk

import serial.tools.list_ports as list_ports

import logger
import text_notification
from colors import Colors


class Initialization:
    def initializeDefaults(self, savePath, outerFrame, readerColor):
        self.initializeColors()
        self.initializeFrequencyPlot(readerColor)
        self.initializeVna()
        self.initializeSecondAxis()
        self.initializeNotes()
        self.initializeDenoise()
        self.initializeAnalysis()
        self.setSavePath(savePath)
        self.findPort()
        self.createUpdateFrequenciesButton(outerFrame)
        if self.AppModule.isDevMode == True:
            self.devModeInitialization()

    def initializeColors(self):
        colors = Colors()
        self.green = colors.green
        self.yellow = colors.yellow
        self.red = colors.red
        self.lightRed = colors.lightRed
        self.white = colors.white

    def initializeFrequencyPlot(self, readerColor):
        self.frequencyPlot = None
        self.frequencyFigure = None
        self.frequencyCanvas = None
        self.frequencyFrame = None
        self.plotFrequencyButton = None
        self.readerColor = readerColor

    def initializeVna(self):
        self.port = None
        self.socket = None
        self.scanMagnitude = []
        self.scanFrequency = []
        self.scanNumber = 100001

    def initializeSecondAxis(self):
        self.secondAxisTitle = None
        self.secondAxisValues = []
        self.secondAxisTime = []

    def initializeNotes(self):
        self.notes = ''
        self.notesTimestamps = []

    def initializeDenoise(self):
        self.denoisePoints = 1
        self.denoiseRadius = 1
        self.denoiseTime = []
        self.denoiseTimeDb = []
        self.denoiseFrequency = []
        self.denoiseTotalMin = []

    def initializeAnalysis(self):
        self.savePath = self.AppModule.savePath
        self.minFrequency = []
        self.minFrequencySpline = []
        self.minFrequencyRaw = []
        self.minFrequencySmooth = []
        self.minDb = []
        self.minDbSpline = []
        self.minDbRaw = []
        self.minDbSmooth = []
        self.time = []

    def initializeContamination(self, outerFrame):
        self.contaminated = False
        self.continuousContamination = 0
        self.createIndicator(outerFrame)
        self.updateContaminationJson(self.white)

    def initializeHarvest(self, outerFrame):
        self.closeToHarvest = False
        self.readyToHarvest = False
        self.inoculatedTime = 1e10
        self.hoursAfterInoculation = 2
        self.closeToHarvestThreshold = 0.005
        self.consecutivePoints = 8
        self.savgolPoints = 51
        self.backwardPoints = 25
        self.harvested = False
        self.continuousHarvest = 0
        self.continuousHarvestReady = 0
        self.createIndicator(outerFrame)
        self.updateHarvestJson(self.green)

    def initializeFoaming(self, airFreq, waterFreq, waterShift):
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

    def setSavePath(self, savePath):
        if not os.path.exists(savePath):
            os.mkdir(savePath)
        self.savePath = rf'{savePath}/{self.readerNumber}{self.folderSuffix}'
        if not self.AppModule.ServerFileShare.disabled:
            self.serverSavePath = rf'{self.AppModule.ServerFileShare.serverLocation}/{self.readerNumber}{self.folderSuffix}'
        else:
            self.serverSavePath = 'incorrect/path'
        self.createFolders()

    def createFolders(self):
        if not os.path.exists(self.serverSavePath) and not self.AppModule.ServerFileShare.disabled:
            os.mkdir(self.serverSavePath)
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)
        if not os.path.exists(f'{self.savePath}/Calibration.csv'):
            if os.path.exists(self.calFileLocation):
                shutil.copy(self.calFileLocation, f'{self.savePath}/Calibration.csv')
            else:
                text_notification.setText(f"No calibration found for \n Reader {self.readerNumber}",
                                          ('Courier', 12, 'bold'), self.AppModule.royalBlue, 'red')
                logger.info(f"No calibration found for Reader {self.readerNumber}")

    def findPort(self):
        if self.AppModule.isDevMode == False:
            portList, attempts = [], 0
            self.pauseUntilUserClicks()
            while portList == [] and attempts <= 3:
                time.sleep(2)
                if self.AppModule.os == "windows":
                    ports = list_ports.comports()
                    portNums = [int(ports[i][0][3:]) for i in range(len(ports))]
                    portList = [num for num in portNums if num not in self.AppModule.ports]
                    if portList != []:
                        self.port = f'COM{max(portList)}'
                        self.AppModule.ports.append(max(portList))
                        return
                else:
                    ports = sp.run('ls /dev/ttyUSB*', shell=True, capture_output=True).stdout.decode(
                        'ascii').strip().splitlines()
                    portList = [port for port in ports if port not in self.AppModule.ports]
                    if portList != []:
                        self.port = portList[-1]
                        self.AppModule.ports.append(max(portList))
                        return
                logger.info(f'Used: {self.AppModule.ports}, found: {portList}')
                tk.messagebox.showinfo(f'Reader {self.readerNumber}',
                                       f'Reader {self.readerNumber}\nNew VNA not found, press OK to try again.')
                attempts += 1
                if attempts > 3:
                    tk.messagebox.showinfo(f'Reader {self.readerNumber}',
                                           f'Reader {self.readerNumber}\nNew VNA not found more than 3 times,\nApp restart required to avoid infinite loop')

            logger.info(f'{self.AppModule.ports}')

    def pauseUntilUserClicks(self):
        tk.messagebox.showinfo(f'Reader {self.readerNumber}',
                               f'Reader {self.readerNumber}\nPress OK when reader {self.readerNumber} is plugged in')
