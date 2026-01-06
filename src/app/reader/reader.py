import logging
import os
import shutil
import tkinter.ttk as ttk

from src.app.helper_methods.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.model.plottable import Plottable
from src.app.use_case.use_case_factory import ContextFactory
from src.app.helper_methods.data_helpers import frequencyToIndex
from src.app.helper_methods.model.result_set.result_set import ResultSet
from src.app.properties.dev_properties import DevProperties
from src.app.reader.algorithm.harvest_algorithm import HarvestAlgorithm
from src.app.reader.analyzer.analyzer import Analyzer
from src.app.reader.analyzer.dev_analyzer import DevAnalyzer
from src.app.reader.analyzer.dev_secondary_axis_tracker import DevSecondaryAxisTracker
from src.app.reader.analyzer.secondary_axis_tracker import SecondaryAxisTracker
from src.app.reader.helpers.plotter import Plotter
from src.app.reader.service.aws_service import AwsService
from src.app.reader.service.dev_aws_service import DevAwsService
from src.app.reader.sib.dev_sib import DevSib
from src.app.reader.sib.sib_interface import SibInterface
from src.app.widget import text_notification
from src.app.widget.indicator import Indicator
from src.app.widget.issues.automated_issue_manager import AutomatedIssueManager


class Reader:
    def __init__(self, globalFileManager, readerNumber, readerPage, sibInterface: SibInterface):
        self.FileManager = ReaderFileManager(globalFileManager.getSavePath(), readerNumber)
        self.HarvestAlgorithm = HarvestAlgorithm(self.FileManager)
        if DevProperties().isDevMode:
            self.AwsService = DevAwsService(self.FileManager, globalFileManager)
            self.Analyzer = DevAnalyzer(self.FileManager, readerNumber, self.HarvestAlgorithm)
            self.SibInterface = DevSib(readerNumber)
        else:
            self.AwsService = AwsService(self.FileManager, globalFileManager)
            self.Analyzer = Analyzer(self.FileManager, self.HarvestAlgorithm)
            self.SibInterface = sibInterface
        self.AutomatedIssueManager = AutomatedIssueManager(self.AwsService, globalFileManager)
        self.ReaderPage = readerPage
        self.finishedEquilibrationPeriod = False

        self.readerNumber = readerNumber
        self.initialize(globalFileManager.getSavePath())
        if DevProperties().isDevMode and DevProperties().useMockSecondaryAxis:
            self.SecondaryAxisTracker = DevSecondaryAxisTracker(self.FileManager.getSecondAxis())
        else:
            self.SecondaryAxisTracker = SecondaryAxisTracker(self.FileManager.getSecondAxis())
        self.Plotter = Plotter(
            readerNumber,
            self.FileManager,
            readerPage.getPlottingFrame(),
            self.SecondaryAxisTracker,
        )
        self.SibInterface.setStartFrequency(ContextFactory().getSibProperties().startFrequency)
        self.SibInterface.setStopFrequency(ContextFactory().getSibProperties().stopFrequency)
        self.yAxisLabel = self.SibInterface.getYAxisLabel()
        self.Indicator = Indicator(readerNumber, self.ReaderPage)
        self.plotFrequencyButton = ttk.Button(
            readerPage.frame,
            text="Real Time Plot",
            command=lambda: self.Plotter.plotFrequencies(
                self.getAnalyzer().ResultSet,
                self.getAnalyzer().zeroPoint,
                self.getAnalyzer().sweepData,
            )
        )
        self.Plotter.ReaderFigureCanvas.showSgi.subscribe(lambda toggle: self.plotFrequencyButton.invoke())

    def getCurrentPlottable(self, denoiseSet) -> Plottable:
        return Plottable(
            self.Analyzer.ResultSet.getDenoiseTimeSmooth(),
            frequencyToIndex(self.Analyzer.zeroPoint, self.Analyzer.ResultSet.getDenoiseFrequencySmooth()),
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
                text_notification.setText("No calibration found.",
                                          ('Courier', 12, 'bold'), foregroundColor='red')
                logging.info(f"No calibration found.", extra={"id": f"Reader {self.readerNumber}"})
