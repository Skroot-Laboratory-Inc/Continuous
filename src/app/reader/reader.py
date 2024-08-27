import logging
import os
import shutil
import tkinter.ttk as ttk

from src.app.aws.aws import AwsBoto3
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import frequencyToIndex
from src.app.model.plottable import Plottable
from src.app.model.result_set import ResultSet
from src.app.properties.dev_properties import DevProperties
from src.app.reader.algorithm.contamination_algorithm import ContaminationAlgorithm
from src.app.reader.algorithm.harvest_algorithm import HarvestAlgorithm
from src.app.reader.analyzer.analyzer import Analyzer
from src.app.reader.analyzer.dev_analyzer import DevAnalyzer
from src.app.reader.helpers.plotter import Plotter
from src.app.reader.reader_interface import ReaderInterface
from src.app.reader.sib.dev_sib import DevSib
from src.app.reader.sib.sib_interface import SibInterface
from src.app.theme.colors import Colors
from src.app.ui_manager.reader_page_allocator import ReaderPageAllocator
from src.app.widget import text_notification
from src.app.widget.indicator import Indicator


class Reader(ReaderInterface):
    def __init__(self, AppModule, readerNumber, readerPageAllocator: ReaderPageAllocator, startFreq, stopFreq, savePath,
                 readerColor, sibInterface: SibInterface, experimentNotes, freqToggleSet):
        self.FileManager = ReaderFileManager(savePath, readerNumber)
        self.ReaderPageAllocator = readerPageAllocator
        self.finishedEquilibrationPeriod = False
        self.colors = Colors()
        self.readerNumber = readerNumber
        self.initialize(savePath)
        self.Aws = AwsBoto3()
        self.ExperimentNotes = experimentNotes
        self.Plotter = Plotter(
            readerColor,
            readerNumber,
            AppModule.denoiseSet,
            self.FileManager,
            self.ExperimentNotes,
            AppModule.guidedSetupForm.getSecondAxisTitle(),
        )
        isDevMode = DevProperties().isDevMode
        if isDevMode:
            self.Analyzer = DevAnalyzer(self.FileManager, readerNumber)
            self.SibInterface = DevSib(readerNumber)
        else:
            self.Analyzer = Analyzer(self.FileManager)
            self.SibInterface = sibInterface
        self.SibInterface.setStartFrequency(startFreq)
        self.SibInterface.setStopFrequency(stopFreq)
        self.yAxisLabel = self.SibInterface.getYAxisLabel()
        self.ContaminationAlgorithm = ContaminationAlgorithm(readerNumber)
        self.Indicator = Indicator(readerNumber, self.ReaderPageAllocator)
        self.HarvestAlgorithm = HarvestAlgorithm(self.FileManager, self.ExperimentNotes, readerNumber, self.Indicator)
        self.Plotter.frequencyFrame = self.ReaderPageAllocator.createPlotFrame(self.readerNumber)
        self.plotFrequencyButton = ttk.Button(
            readerPageAllocator.readerPage,
            text="Real Time Plot",
            command=lambda: self.Plotter.plotFrequencies(
                self.getAnalyzer().ResultSet,
                self.getAnalyzer().zeroPoint,
                self.getAnalyzer().sweepData,
                self.freqToggleSet
            )
        )
        freqToggleSet.subscribe(lambda toggle: self.setViewToggle(toggle))

    def addToPdf(self, pdf, x, y, indicatorRadius, totalWidth, totalHeight):
        pdf.placeImage(
            self.FileManager.getReaderPlotJpg(),
            x,
            y,
            totalWidth-indicatorRadius*3,
            totalHeight)
        if not self.HarvestAlgorithm.getStatus():
            pdf.drawCircle(totalWidth-indicatorRadius*2, indicatorRadius*2, indicatorRadius, 'green')
        else:
            pdf.drawCircle(totalWidth-indicatorRadius*2, indicatorRadius*2, indicatorRadius, 'red')

    def addInoculationMenuBar(self, menu):
        menu.add_command(
            label=f"Reader {self.readerNumber} Inoculated",
            command=lambda: self.HarvestAlgorithm.updateInoculationForReader(self.Analyzer.ResultSet)
        )

    def addSecondAxisMenubar(self, menu):
        menu.add_command(
            label=f"Reader {self.readerNumber}",
            command=lambda: self.Plotter.SecondAxis.typeSecondAxisValues(self.Analyzer.ResultSet.getTime())
        )

    def addExperimentNotesMenubar(self, menu):
        menu.add_command(
            label=f"Reader {self.readerNumber}",
            command=lambda:
            self.Plotter.ExperimentNotes.typeExperimentNotes(
                self.readerNumber,
                self.getAnalyzer().ResultSet,
            )
        )

    def getCurrentPlottable(self, denoiseSet) -> Plottable:
        if denoiseSet:
            return Plottable(
                self.Analyzer.ResultSet.getDenoiseTimeSmooth(),
                frequencyToIndex(self.Analyzer.zeroPoint, self.Analyzer.ResultSet.getDenoiseFrequencySmooth()),
                self.Plotter.readerColor,
            )
        else:
            return Plottable(
                self.Analyzer.ResultSet.getTime(),
                frequencyToIndex(self.Analyzer.zeroPoint, self.Analyzer.ResultSet.getDenoiseFrequency()),
                self.Plotter.readerColor,
            )

    def getAnalyzer(self) -> Analyzer:
        return self.Analyzer

    def getResultSet(self) -> ResultSet:
        return self.Analyzer.ResultSet

    def getZeroPoint(self):
        return self.Analyzer.zeroPoint

    def resetReaderRun(self):
        self.Analyzer.resetRun()

    """ End of required public facing functions. """

    def setViewToggle(self, toggle):
        self.freqToggleSet = toggle
        # Changes to the UI need to be done in the UI thread, where the button was placed, otherwise weird issues occur.
        self.plotFrequencyButton.invoke()

    def initialize(self, savePath):
        if not os.path.exists(savePath):
            os.mkdir(savePath)
        self.createFolders()

    def createFolders(self):
        if not os.path.exists(self.FileManager.getReaderSavePath()):
            os.mkdir(self.FileManager.getReaderSavePath())
        if not os.path.exists(self.FileManager.getCalibrationLocalLocation()):
            if os.path.exists(self.FileManager.getCalibrationGlobalLocation()):
                shutil.copy(self.FileManager.getCalibrationGlobalLocation(),
                            self.FileManager.getCalibrationLocalLocation())
            else:
                text_notification.setText(f"No calibration found for \n Reader {self.readerNumber}",
                                          ('Courier', 12, 'bold'), self.colors.primaryColor, 'red')
                logging.info(f"No calibration found for Reader {self.readerNumber}")
