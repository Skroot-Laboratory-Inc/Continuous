import logging
import math
import threading
import time
from typing import Callable

import numpy as np

from src.app.custom_exceptions.analysis_exception import ZeroPointException, AnalysisException
from src.app.custom_exceptions.sib_exception import SIBReconnectException
from src.app.helper_methods.data_helpers import frequencyToIndex
from src.app.helper_methods.helper_functions import getZeroPoint
from src.app.model.issue.issue import Issue
from src.app.model.issue.potential_issue import PotentialIssue
from src.app.model.setup_reader_form_input import SetupReaderFormInput
from src.app.properties.common_properties import CommonProperties
from src.app.properties.dev_properties import DevProperties
from src.app.properties.issue_properties import IssueProperties
from src.app.reader.reader import Reader
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification
from src.resources.sibcontrol.sibcontrol import SIBException, SIBConnectionError


class ReaderThreadManager:
    def __init__(self, reader: Reader, rootManager: RootManager, guidedSetupForm: SetupReaderFormInput,
                 resetRunFunc, issueOccurredFn: Callable):
        self.guidedSetupForm = guidedSetupForm
        self.issueOccurredFn = issueOccurredFn
        self.scanRate = guidedSetupForm.getScanRate()
        self.equilibrationTime = guidedSetupForm.getEquilibrationTime()
        self.thread = threading.Thread(target=self.mainLoop, args=(reader,), daemon=True)
        self.Timer = reader.ReaderPageAllocator.getTimer()
        self.isDevMode = DevProperties().isDevMode
        self.RootManager = rootManager
        self.Reader = reader
        # Current Issues is supposed to be a dict of all issues used for updating text_notification on successful runs.
        # Needs fixing.
        self.currentIssues = {}

        self.finishedEquilibrationPeriod = False
        self.disableFullSaveFiles = CommonProperties().disableSaveFullFiles
        self.denoiseSet = CommonProperties().denoiseSet
        self.Colors = Colors()
        self.resetRunFunc = resetRunFunc

    def startReaderLoop(self, user: str):
        self.Reader.ReaderPageAllocator.getReaderFrame().kpiForm.setConstants(
            self.guidedSetupForm.getLotId(),
            user,
            self.guidedSetupForm.getPumpFlowRate(),
        )
        self.thread.start()

    def checkZeroPoint(self):
        try:
            if len(self.Reader.getResultSet().getTime()) != 0:
                lastTimePoint = self.Reader.getResultSet().getTime()[-1]
                if lastTimePoint >= self.equilibrationTime and not self.Reader.finishedEquilibrationPeriod:
                    zeroPoint = getZeroPoint(
                        self.equilibrationTime,
                        self.Reader.getResultSet().getMaxFrequencySmooth())
                    if zeroPoint == np.nan:
                        text_notification.setText(
                            f"Failed to set zero point for {self.Reader.readerNumber}. SGI values unreliable.")
                        logging.info(f"Failed to set zero point, SGI values unreliable.",
                                     extra={"id": f"Reader {self.Reader.readerNumber}"})
                        zeroPoint = 1
                    self.Reader.getAnalyzer().setZeroPoint(zeroPoint)
                    self.Reader.finishedEquilibrationPeriod = True
                    self.Reader.Plotter.ReaderFigureCanvas.reachedEquilibration = True
                    self.Reader.Plotter.ReaderFigureCanvas.showSgi.on_next(True)
                    logging.info(f"Zero Point Set for reader {self.Reader.readerNumber}: {zeroPoint} MHz",
                                 extra={"id": f"Reader {self.Reader.readerNumber}"})
                    self.Reader.resetReaderRun()
                    self.finishedEquilibrationPeriod = True
        except:
            raise ZeroPointException(
                f"Failed to find the zero point for reader {self.Reader.readerNumber}, last 5 points: {self.Reader.getResultSet().getMaxFrequencySmooth()[-5:]}")

    def takeSweep(self):
        reader = self.Reader
        try:
            reader.Indicator.changeIndicatorYellow()
            self.checkZeroPoint()
            sweepData = reader.SibInterface.takeScan(
                reader.FileManager.getCurrentScan(),
                self.disableFullSaveFiles,
            )
            reader.getAnalyzer().analyzeScan(sweepData, self.denoiseSet)
            reader.plotFrequencyButton.invoke()  # any changes to GUI must be in common_modules thread
            reader.HarvestAlgorithm.check(reader.getResultSet())
            if reader.HarvestAlgorithm.currentHarvestPrediction != 0 and not np.isnan(reader.HarvestAlgorithm.currentHarvestPrediction):
                reader.ReaderPageAllocator.getReaderFrame().kpiForm.setSaturation(
                    reader.HarvestAlgorithm.currentHarvestPrediction,
                )
            else:
                reader.ReaderPageAllocator.getReaderFrame().kpiForm.setSaturation(
                    "No Estimate",
                )
            if reader.finishedEquilibrationPeriod:
                reader.ReaderPageAllocator.getReaderFrame().kpiForm.setSgi(
                    frequencyToIndex(self.Reader.Analyzer.zeroPoint,
                                     self.Reader.Analyzer.ResultSet.getDenoiseFrequencySmooth())[-1],
                )
            reader.Indicator.changeIndicatorGreen()
            if reader.readerNumber in self.currentIssues and not self.currentIssues[reader.readerNumber].resolved:
                self.currentIssues[reader.readerNumber].resolveIssue()
                if type(self.currentIssues[reader.readerNumber]) is Issue:
                    reader.AutomatedIssueManager.updateIssue(self.currentIssues[reader.readerNumber])
                del self.currentIssues[reader.readerNumber]
        finally:
            reader.Analyzer.createAnalyzedFiles()
            if reader.finishedEquilibrationPeriod:
                reader.AwsService.uploadExperimentFilesOnInterval(
                    reader.FileManager.getCurrentScanNumber(),
                    self.guidedSetupForm,
                    reader.ReaderPageAllocator.getReaderFrame().kpiForm.saturationTime.get(),
                    reader.AutomatedIssueManager.hasOpenIssues()
                )

    def mainLoop(self, reader):
        if self.isDevMode:
            self.scanRate = DevProperties().scanRate
        self.thread.shutdown_flag = threading.Event()

        while not self.thread.shutdown_flag.is_set():
            startTime = time.time()
            try:
                try:
                    self.takeSweep()
                except SIBConnectionError:
                    if reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[reader.readerNumber] = self.currentIssues[
                                reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveHardwareIssue,
                            f"Automated - Reader Connection Error On Reader {reader.readerNumber}.",
                            reader.AutomatedIssueManager.createIssue,
                        )
                    reader.Indicator.changeIndicatorRed()
                    reader.getAnalyzer().recordFailedScan()
                    logging.exception(
                        f'Connection Error: Failed to take scan {reader.FileManager.getCurrentScanNumber()}',
                        extra={"id": f"Reader {reader.readerNumber}"})
                    text_notification.setText(f"Sweep Failed, check reader {reader.readerNumber} connection.")
                except SIBReconnectException:
                    if reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[reader.readerNumber] = self.currentIssues[
                                reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveHardwareIssue,
                            f"Automated - Hardware Issue Identified On Reader {reader.readerNumber}.",
                            reader.AutomatedIssueManager.createIssue,
                        )
                    reader.Indicator.changeIndicatorRed()
                    reader.getAnalyzer().recordFailedScan()
                    logging.exception(
                        f'Failed to take scan {reader.FileManager.getCurrentScanNumber()}, but reconnected successfully',
                        extra={"id": f"Reader {reader.readerNumber}"})
                    text_notification.setText(
                        f"Sweep failed for reader {reader.readerNumber}, reconnection successful.")
                except SIBException:
                    if reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[reader.readerNumber] = self.currentIssues[
                                reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveHardwareIssue,
                            f"Automated - Hardware Issue Identified On Reader {reader.readerNumber}.",
                            reader.AutomatedIssueManager.createIssue,
                        )
                    reader.Indicator.changeIndicatorRed()
                    reader.getAnalyzer().recordFailedScan()
                    logging.exception(
                        f'Hardware Problem: Failed to take scan {reader.FileManager.getCurrentScanNumber()}',
                        extra={"id": f"Reader {reader.readerNumber}"})
                    text_notification.setText(
                        f"Sweep Failed With Hardware Cause for reader {reader.readerNumber}, contact a Skroot representative if the issue persists.")
                except AnalysisException:
                    if reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[reader.readerNumber] = self.currentIssues[
                                reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveAnalysisIssue,
                            f"Automated - Analysis Failed On Reader {reader.readerNumber}.",
                            reader.AutomatedIssueManager.createIssue,
                        )
                    reader.Indicator.changeIndicatorRed()
                    logging.exception(
                        f'Error Analyzing Data, failed to analyze scan {reader.FileManager.getCurrentScanNumber()}',
                        extra={"id": f"Reader {reader.readerNumber}"})
                    text_notification.setText(
                        f"Sweep Analysis Failed, check sensor placement on reader {reader.readerNumber}.")
                finally:
                    self.Timer.updateTime()
                    reader.FileManager.incrementScanNumber(self.guidedSetupForm.getScanRate())
                if not self.issueOccurredFn():
                    text_notification.setText(f"Reader {self.Reader.readerNumber} successfully recorded a sweep.")
            except:
                logging.exception('Unknown error has occurred', extra={"id": f"Reader {reader.readerNumber}"})
            finally:
                currentTime = time.time()
                if self.isDevMode and DevProperties().enforceScanRate:
                    pass
                else:
                    self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
        text_notification.setText(f"Reader {reader.readerNumber} finished run.")
        if reader.finishedEquilibrationPeriod:
            reader.AwsService.uploadFinalExperimentFiles(
                self.guidedSetupForm,
                reader.ReaderPageAllocator.getReaderFrame().kpiForm.saturationTime.get(),
            )
        self.resetRunFunc(reader.readerNumber)
        logging.info(f'Finished run.', extra={"id": f"Reader {reader.readerNumber}"})

    def checkIfScanTookTooLong(self, timeTaken):
        if timeTaken > self.scanRate * 60:
            self.scanRate = math.ceil(timeTaken / 60)
            text_notification.setText(f"Took too long to take scans. Scan rate now {self.scanRate}.")
            logging.info(f'{timeTaken} seconds to take scan. Scan rate now {self.scanRate}.',
                         extra={"id": f"Reader {self.Reader.readerNumber}"})

    def waitUntilNextScan(self, currentTime, startTime):
        while currentTime - startTime < self.scanRate * 60:
            if self.thread.shutdown_flag.is_set():
                logging.info('Cancelling data collection due to stop button pressed',
                             extra={"id": f"Reader {self.Reader.readerNumber}"})
                break
            time.sleep(0.05)
            self.Timer.updateTime()
            currentTime = time.time()
