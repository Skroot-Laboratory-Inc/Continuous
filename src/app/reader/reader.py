import logging
import os
import shutil

from src.app.algorithm.contamination_algorithm import ContaminationAlgorithm
from src.app.algorithm.harvest_algorithm import HarvestAlgorithm
from src.app.aws.aws import AwsBoto3
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.initialization.dev import ReaderDevMode
from src.app.reader.analyzer import Analyzer
from src.app.reader.plotting import Plotting
from src.app.sib.reader_interface import ReaderInterface
from src.app.widget import text_notification


class Reader(ReaderDevMode):
    def __init__(self, AppModule, readerNumber, outerFrame, totalNumberOfReaders, startFreq, stopFreq,
                 scanRate, savePath, readerColor, readerInterface: ReaderInterface):
        self.FileManager = ReaderFileManager(savePath, readerNumber)
        self.AppModule = AppModule
        self.readerNumber = readerNumber
        self.totalNumberOfReaders = totalNumberOfReaders
        self.initializeReaderFolders(savePath)
        if not self.AppModule.DevMode.isDevMode:
            readerInterface.setStartFrequency(startFreq)
            readerInterface.setStopFrequency(stopFreq)
        self.ReaderInterface = readerInterface
        self.yAxisLabel = readerInterface.getYAxisLabel()
        self.Aws = AwsBoto3()
        self.scanMagnitude = []
        self.scanFrequency = []
        self.scanRate = scanRate
        Plotting.__init__(self, readerColor, outerFrame, readerNumber, AppModule, self.FileManager, self.AppModule.secondAxisTitle)
        self.Analyzer = Analyzer(self.FileManager)
        ReaderDevMode.__init__(self, AppModule, readerNumber)
        self.ContaminationAlgorithm = ContaminationAlgorithm(outerFrame, readerNumber)
        self.HarvestAlgorithm = HarvestAlgorithm(outerFrame, self.FileManager)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)
        self.AppModule.freqToggleSet.subscribe(lambda toggle: self.setToggle(toggle))

    def getAnalyzer(self):
        return self.Analyzer

    def addToPdf(self, pdf, currentX, currentY, labelWidth, plotWidth, plotHeight, notesWidth, paddingY):
        pdf.placeImage(self.FileManager.getReaderPlotJpg(), currentX, currentY, plotWidth, plotHeight)
        currentX += plotWidth
        if not self.HarvestAlgorithm.getStatus():
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

    def addInoculationMenuBar(self, menu):
        menu.add_command(label=f"Reader {self.readerNumber} Inoculated", command=lambda: self.HarvestAlgorithm.updateInoculation(self.Analyzer))

    def resetReaderRun(self):
        self.Analyzer.resetRun()

