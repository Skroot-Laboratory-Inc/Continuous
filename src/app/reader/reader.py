import json
import logging
import os
import shutil
import socket

import paramiko
from scp import SCPClient

from src.app.algorithm.algorithms import ContaminationAlgorithm, HarvestAlgorithm
from src.app.aws.aws import AwsBoto3
from src.app.helper.helper_functions import getOperatingSystem
from src.app.initialization.dev import ReaderDevMode
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.reader.analysis import Analysis
from src.app.reader.plotting import Plotting
from src.app.sib.reader_interface import ReaderInterface
from src.app.widget import text_notification


class Reader(ContaminationAlgorithm, HarvestAlgorithm, ReaderDevMode):
    def __init__(self, AppModule, readerNumber, outerFrame, totalNumberOfReaders, startFreq, stopFreq,
                 scanRate, savePath, readerColor, ReaderInterface: ReaderInterface):
        self.FileManager = ReaderFileManager(savePath, readerNumber)
        self.AppModule = AppModule
        self.readerNumber = readerNumber
        self.totalNumberOfReaders = totalNumberOfReaders
        self.initializeReaderFolders(savePath)
        if not self.AppModule.DevMode.isDevMode:
            ReaderInterface.setStartFrequency(startFreq)
            ReaderInterface.setStopFrequency(stopFreq)
        self.ReaderInterface = ReaderInterface
        if not AppModule.DevMode.isDevMode:
            self.yAxisLabel = ReaderInterface.yAxisLabel
        else:
            self.yAxisLabel = "Signal Strength (Unitless)"
        self.Aws = AwsBoto3()
        self.scanMagnitude = []
        self.scanFrequency = []
        self.scanRate = scanRate
        Plotting.__init__(self, readerColor, outerFrame, readerNumber, AppModule, self.FileManager, self.AppModule.secondAxisTitle)
        Analysis.__init__(self, self.FileManager)
        ReaderDevMode.__init__(self, AppModule, readerNumber)
        ContaminationAlgorithm.__init__(self, outerFrame, AppModule, readerNumber)
        HarvestAlgorithm.__init__(self, outerFrame, AppModule)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)
        self.AppModule.freqToggleSet.subscribe(lambda toggle: self.setToggle(toggle))

    def addToPdf(self, pdf, currentX, currentY, labelWidth, plotWidth, plotHeight, notesWidth, paddingY):
        pdf.placeImage(self.FileManager.getReaderPlotJpg(), currentX, currentY, plotWidth, plotHeight)
        currentX += plotWidth
        if not self.harvested:
            pdf.drawCircle(currentX, currentY, 0.02, 'green')
        else:
            pdf.drawCircle(currentX, currentY, 0.02, 'red')
        return currentX, currentY

    def initializeReaderFolders(self, savePath):
        self.setSavePath(savePath)

    def setSavePath(self, savePath):
        if not os.path.exists(savePath):
            os.mkdir(savePath)
        self.createFolders()

    def createFolders(self):
        if not os.path.exists(self.FileManager.getReaderSavePath()):
            os.mkdir(self.FileManager.getReaderSavePath())
        if not os.path.exists(self.FileManager.getCalibrationLocalLocation()):
            if os.path.exists(self.FileManager.getCalibrationGlobalLocation()):
                shutil.copy(self.FileManager.getCalibrationGlobalLocation(), self.FileManager.getCalibrationLocalLocation())
            else:
                text_notification.setText(f"No calibration found for \n Reader {self.readerNumber}",
                                          ('Courier', 12, 'bold'), self.AppModule.primaryColor, 'red')
                logging.info(f"No calibration found for Reader {self.readerNumber}")

    def resetReaderRun(self):
        self.time = self.time[-1:]
        self.timestamp = self.timestamp[-1:]
        self.filenames = self.filenames[-1:]
        self.denoiseTime = self.denoiseTime[-1:]
        self.denoiseTimeSmooth = self.denoiseTimeSmooth[-1:]
        self.maxFrequency = self.maxFrequency[-1:]
        self.maxFrequencySmooth = self.maxFrequencySmooth[-1:]
        self.denoiseFrequency = self.denoiseFrequency[-1:]
        self.denoiseFrequencySmooth = self.denoiseFrequencySmooth[-1:]
        self.maxVoltsSmooth = self.maxVoltsSmooth[-1:]

