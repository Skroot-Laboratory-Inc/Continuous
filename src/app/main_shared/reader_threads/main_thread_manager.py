import csv
import logging
import math
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import List

import numpy as np
from reactivex.subject import BehaviorSubject
from sibcontrol import SIBConnectionError, SIBException

from src.app.exception.analysis_exception import ZeroPointException, AnalysisException
from src.app.exception.sib_exception import SIBReconnectException
from src.app.helper.helper_functions import frequencyToIndex
from src.app.main_shared.reader_threads.end_experiment_file_copier import EndExperimentFileCopier
from src.app.main_shared.service.aws_service import AwsService
from src.app.main_shared.service.dev_aws_service import DevAwsService
from src.app.model.guided_setup_input import GuidedSetupInput
from src.app.properties.dev_properties import DevProperties
from src.app.reader.reader import Reader
from src.app.theme.color_cycler import ColorCycler
from src.app.theme.colors import Colors
from src.app.widget import text_notification
from src.app.widget.pdf import generatePdf
from src.app.widget.timer import RunningTimer


class MainThreadManager:
    def __init__(self, denoiseSet, disableFullSaveFiles, root, major_version, minor_version, globalFileManager, readerPlotFrame, summaryFigureCanvas, resetRunFunc, guidedSetupForm: GuidedSetupInput):
        self.guidedSetupForm = guidedSetupForm
        self.scanRate = guidedSetupForm.getScanRate()
        self.equilibrationTime = guidedSetupForm.getEquilibrationTime()
        self.Readers = []
        self.thread = threading.Thread(target=self.mainLoop, args=(), daemon=True)
        self.Timer = RunningTimer()
        self.SummaryFigureCanvas = summaryFigureCanvas
        self.readerPlotFrame = readerPlotFrame
        self.isDevMode = DevProperties().isDevMode
        self.freqToggleSet = BehaviorSubject("Signal Check")
        self.denoiseSet = denoiseSet
        self.GlobalFileManager = globalFileManager
        self.root = root
        self.finishedEquilibrationPeriod = False
        self.disableFullSaveFiles = disableFullSaveFiles
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.Colors = Colors()
        self.summaryFrame = tk.Frame(self.readerPlotFrame, bg=self.Colors.secondaryColor, bd=0)
        self.summaryPlotButton = ttk.Button(self.readerPlotFrame,
                                            text="Summary Plot Update",
                                            command=lambda: self.plotSummary(self.summaryFrame))
        self.ColorCycler = ColorCycler()

        if self.isDevMode:
            self.AwsService = DevAwsService(root, major_version, minor_version, globalFileManager)
        else:
            self.AwsService = AwsService(root, major_version, minor_version, globalFileManager)
        self.Colors = Colors()
        self.resetRunFunc = resetRunFunc

    def startReaderLoop(self, Readers: List[Reader]):
        self.Readers = Readers
        self.thread.start()

    def mainLoop(self):
        self.FileCopier = EndExperimentFileCopier(self.GlobalFileManager)
        if self.isDevMode:
            self.guidedSetupForm.scanRate = DevProperties().scanRate
        self.thread.shutdown_flag = threading.Event()

        while not self.thread.shutdown_flag.is_set():
            errorOccurredWhileTakingScans = False
            startTime = time.time()
            try:
                for Reader in self.Readers:
                    try:
                        Reader.Indicator.changeIndicatorYellow()
                        sweepData = Reader.SibInterface.takeScan(Reader.FileManager.getCurrentScan(),
                                                                 self.disableFullSaveFiles)
                        Reader.getAnalyzer().analyzeScan(sweepData, self.denoiseSet)
                        try:
                            if Reader.getResultSet().getTime()[-1] >= self.equilibrationTime and not self.finishedEquilibrationPeriod:
                                if (self.equilibrationTime == 0 and
                                        Reader.getResultSet().getMaxFrequencySmooth()[-1] != np.nan
                                and Reader.getResultSet().getMaxFrequencySmooth()[-1] != 0):
                                    zeroPoint = Reader.getResultSet().getMaxFrequencySmooth()[-1]
                                elif (self.equilibrationTime == 0 and
                                      (Reader.getResultSet().getMaxFrequencySmooth()[-1] == np.nan or Reader.getResultSet().getMaxFrequencySmooth()[-1] == 0)):
                                    raise Exception()
                                else:
                                    zeroPoint = np.nanmean(Reader.getResultSet().getMaxFrequencySmooth()[-5:])
                                Reader.getAnalyzer().setZeroPoint(zeroPoint)
                                self.freqToggleSet.on_next("SGI")
                                self.finishedEquilibrationPeriod = True
                                logging.info(f"Zero Point Set for reader {Reader.readerNumber}: {zeroPoint} MHz")
                                Reader.resetReaderRun()
                        except:
                            raise ZeroPointException(
                                f"Failed to find the zero point for reader {Reader.readerNumber}, last 5 points: {Reader.getResultSet().getMaxFrequencySmooth()[-5:]}")
                        Reader.plotFrequencyButton.invoke()  # any changes to GUI must be in main_shared thread
                        Reader.Analyzer.createAnalyzedFiles()
                        # Reader.ContaminationAlgorithm.check(Reader.getResultSet())
                        # Reader.HarvestAlgorithm.check(Reader.getResultSet())
                        Reader.Indicator.changeIndicatorGreen()
                    except SIBConnectionError:
                        errorOccurredWhileTakingScans = True
                        Reader.Indicator.changeIndicatorRed()
                        Reader.getAnalyzer().recordFailedScan()
                        logging.exception(
                            f'Connection Error: Reader {Reader.readerNumber} failed to take scan {Reader.FileManager.getCurrentScanNumber()}')
                        text_notification.setText(f"Sweep Failed, check reader {Reader.readerNumber} connection.")
                    except SIBReconnectException:
                        errorOccurredWhileTakingScans = True
                        Reader.Indicator.changeIndicatorRed()
                        Reader.getAnalyzer().recordFailedScan()
                        logging.exception(
                            f'Reader {Reader.readerNumber} failed to take scan {Reader.FileManager.getCurrentScanNumber()}, but reconnected successfully')
                        text_notification.setText(
                            f"Sweep failed for reader {Reader.readerNumber}, SIB reconnection was successful.")
                    except SIBException:
                        errorOccurredWhileTakingScans = True
                        Reader.Indicator.changeIndicatorRed()
                        Reader.getAnalyzer().recordFailedScan()
                        logging.exception(
                            f'Hardware Problem: Reader {Reader.readerNumber} failed to take scan {Reader.FileManager.getCurrentScanNumber()}')
                        text_notification.setText(
                            f"Sweep Failed With Hardware Cause for reader {Reader.readerNumber}, contact a Skroot representative if the issue persists.")
                    except AnalysisException:
                        errorOccurredWhileTakingScans = True
                        Reader.Indicator.changeIndicatorRed()
                        logging.exception(f'Error Analyzing Data, Reader {Reader.readerNumber} failed to analyze scan {Reader.FileManager.getCurrentScanNumber()}')
                        text_notification.setText(f"Sweep Analysis Failed, check sensor placement on reader {Reader.readerNumber}.")
                    finally:
                        self.Timer.updateTime()
                        Reader.FileManager.incrementScanNumber(self.scanRate)
                if self.finishedEquilibrationPeriod:
                    self.createSummaryAnalyzedFile()
                    self.summaryPlotButton.invoke()  # any changes to GUI must be in main_shared thread
                    generatePdf(self.Readers,
                                self.GlobalFileManager.getSetupForm(),
                                self.GlobalFileManager.getSummaryFigure(),
                                self.GlobalFileManager.getSummaryPdf())
                    self.AwsService.uploadExperimentFilesOnInterval(
                        self.Readers[0].FileManager.getCurrentScanNumber(),
                        self.guidedSetupForm,
                    )
                if not errorOccurredWhileTakingScans:
                    text_notification.setText("All readers successfully recorded data.")
            except:
                logging.exception('Unknown error has occurred')
            finally:
                currentTime = time.time()
                self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
        text_notification.setText("Experiment Ended.",
                                  ('Courier', 9, 'bold'),
                                  self.Colors.primaryColor,
                                  self.Colors.secondaryColor)
        self.resetRunFunc()
        logging.info('Experiment Ended')

    def checkIfScanTookTooLong(self, timeTaken):
        if timeTaken > self.scanRate * 60:
            self.scanRate = math.ceil(timeTaken / 60)
            text_notification.setText(f"Took too long to take scans \nScan rate now {self.scanRate}.")
            logging.info(f'{timeTaken} seconds to take ALL scans')
            logging.info(f"Took too long to take scans \nScan rate now {self.scanRate}.")

    def waitUntilNextScan(self, currentTime, startTime):
        while currentTime - startTime < self.scanRate * 60:
            if self.thread.shutdown_flag.is_set():
                logging.info('Cancelling data collection due to stop button pressed')
                break
            time.sleep(0.05)
            self.Timer.updateTime()
            currentTime = time.time()

    def onClosing(self):
        if tk.messagebox.askokcancel("Exit", "Are you sure you want to close the program?"):
            self.finalizeRunResults()
            self.root.destroy()

    def finalizeRunResults(self):
        if self.finishedEquilibrationPeriod:
            self.AwsService.uploadFinalExperimentFiles(self.guidedSetupForm)
        for Reader in self.Readers:
            try:
                Reader.SibInterface.close()
            except AttributeError:
                Reader.socket = None
                logging.exception(f'Failed to close Reader {Reader.readerNumber} socket')
        if self.Readers:
            self.FileCopier.copyFilesToDebuggingFolder(self.Readers)
            self.FileCopier.copyFilesToAnalysisFolder(self.Readers)

    def createSummaryAnalyzedFile(self):
        rowHeaders = ['Time (hours)']
        rowData = [self.Readers[0].getResultSet().getTime()]
        with open(self.GlobalFileManager.getSummaryAnalyzed(), 'w', newline='') as f:
            writer = csv.writer(f)
            for Reader in self.Readers:
                rowHeaders.append(f'Reader {Reader.readerNumber} SGI')
                readerSGI = frequencyToIndex(
                    Reader.getZeroPoint(),
                    Reader.getResultSet().getMaxFrequencySmooth()
                )
                rowData.append(readerSGI)
            writer.writerow(rowHeaders)
            # array transpose converts it to write columns instead of rows
            writer.writerows(np.array(rowData).transpose())
        return

    def plotSummary(self, frame):
        try:
            self.SummaryFigureCanvas.redrawPlot()
            self.ColorCycler.reset()
            for Reader in self.Readers:
                readerPlottable = Reader.getCurrentPlottable(self.denoiseSet)
                self.SummaryFigureCanvas.scatter(
                    readerPlottable.getXValues(),
                    readerPlottable.getYValues(),
                    20,
                    readerPlottable.getColor(),
                )
            self.SummaryFigureCanvas.saveAs(self.GlobalFileManager.getSummaryFigure())
            self.SummaryFigureCanvas.drawCanvas(frame)
        except:
            logging.exception("Failed to generate summaryPlot")
