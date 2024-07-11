import logging
import os
import shutil
import tkinter.ttk as ttk

from src.app.reader.algorithm.contamination_algorithm import ContaminationAlgorithm
from src.app.reader.algorithm.harvest_algorithm import HarvestAlgorithm
from src.app.aws.aws import AwsBoto3
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import frequencyToIndex
from src.app.model.plottable import Plottable
from src.app.model.result_set import ResultSet
from src.app.reader.analyzer.analyzer import Analyzer
from src.app.reader.helpers.experiment_notes import ExperimentNotes
from src.app.reader.helpers.plotter import Plotter
from src.app.reader.reader_interface import ReaderInterface
from src.app.reader.sib.sib_interface import SibInterface
from src.app.theme.colors import Colors
from src.app.widget import text_notification
from src.app.widget.indicator import Indicator


class DevReader(ReaderInterface):
    def __init__(self, AppModule, readerNumber, outerFrame, totalNumberOfReaders, startFreq, stopFreq, savePath, readerColor, readerInterface: SibInterface):
        self.FileManager = ReaderFileManager(savePath, readerNumber)
        self.colors = Colors()
        self.readerNumber = readerNumber
        self.initialize(savePath)
        if not AppModule.DevProperties.isDevMode:
            readerInterface.setStartFrequency(startFreq)
            readerInterface.setStopFrequency(stopFreq)
        self.SibInterface = readerInterface
        self.yAxisLabel = readerInterface.getYAxisLabel()
        self.Aws = AwsBoto3()
        self.ExperimentNotes = ExperimentNotes(readerNumber, self.FileManager)
        self.Plotter = Plotter(
            readerColor,
            readerNumber,
            AppModule.denoiseSet,
            self.FileManager,
            self.ExperimentNotes,
            AppModule.secondAxisTitle,
        )
        self.Analyzer = Analyzer(self.FileManager)
        self.ContaminationAlgorithm = ContaminationAlgorithm(readerNumber)
        self.Indicator = Indicator(totalNumberOfReaders, readerNumber)
        self.Indicator.createIndicator(outerFrame)
        self.HarvestAlgorithm = HarvestAlgorithm(self.FileManager, self.ExperimentNotes, readerNumber, self.Indicator)
        self.Plotter.createFrequencyFrame(outerFrame, totalNumberOfReaders)
        self.plotFrequencyButton = ttk.Button(
            outerFrame,
            text="Real Time Plot",
            command=lambda: self.Plotter.plotFrequencies(
                self.getAnalyzer().ResultSet,
                self.getAnalyzer().zeroPoint,
                self.getAnalyzer().sweepData,
                self.freqToggleSet
            )
        )
        AppModule.freqToggleSet.subscribe(lambda toggle: self.setViewToggle(toggle))

    def addToPdf(self, pdf, currentX, currentY, labelWidth, plotWidth, plotHeight, notesWidth, paddingY):
        pdf.placeImage(self.FileManager.getReaderPlotJpg(), currentX, currentY, plotWidth, plotHeight)
        currentX += plotWidth
        if not self.HarvestAlgorithm.getStatus():
            pdf.drawCircle(currentX, currentY, 0.02, 'green')
        else:
            pdf.drawCircle(currentX, currentY, 0.02, 'red')
        return currentX, currentY

    def addInoculationMenuBar(self, menu):
        menu.add_command(
            label=f"Reader {self.readerNumber} Inoculated",
            command=lambda: self.HarvestAlgorithm.updateInoculation(self.Analyzer)
        )

    def addSecondAxisMenubar(self, menu):
        menu.add_command(
            label=f"Reader {self.readerNumber}",
            command=lambda: self.Plotter.SecondAxis.typeSecondAxisValues(self.Analyzer.ResultSet.getTime())
        )

    def addExperimentNotesMenubar(self, menu):
        menu.add_command(
            label=f"Reader {self.readerNumber}",
            command=lambda: self.Plotter.ExperimentNotes.typeExperimentNotes(self.getAnalyzer().ResultSet)
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

    """ End of required publicly facing functions. """

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
