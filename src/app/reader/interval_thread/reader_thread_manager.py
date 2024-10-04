import logging
import math
import threading
import time
from typing import Callable

import numpy as np
from sibcontrol import SIBConnectionError, SIBException

from src.app.exception.analysis_exception import ZeroPointException, AnalysisException
from src.app.exception.sib_exception import SIBReconnectException
from src.app.helper.helper_functions import getZeroPoint
from src.app.model.setup_reader_form_input import SetupReaderFormInput
from src.app.model.issue.issue import Issue
from src.app.model.issue.potential_issue import PotentialIssue
from src.app.properties.common_properties import CommonProperties
from src.app.properties.dev_properties import DevProperties
from src.app.properties.issue_properties import IssueProperties
from src.app.reader.reader import Reader
from src.app.theme.colors import Colors
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification


class ReaderThreadManager:
    def __init__(self, reader: Reader, rootManager: RootManager, guidedSetupForm: SetupReaderFormInput, freqToggleSet, resetRunFunc, issueOccurredFn: Callable):
        self.guidedSetupForm = guidedSetupForm
        self.issueOccurredFn = issueOccurredFn
        self.scanRate = guidedSetupForm.getScanRate()
        self.equilibrationTime = guidedSetupForm.getEquilibrationTime()
        self.thread = threading.Thread(target=self.mainLoop, args=(), daemon=True)
        self.Timer = reader.ReaderPageAllocator.getTimer(reader.readerNumber)
        self.isDevMode = DevProperties().isDevMode
        self.freqToggleSet = freqToggleSet
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

    def startReaderLoop(self):
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
                        logging.info(f"Failed to set zero point for {self.Reader.readerNumber}. SGI values unreliable.")
                        zeroPoint = 1
                    self.Reader.getAnalyzer().setZeroPoint(zeroPoint)
                    self.Reader.finishedEquilibrationPeriod = True
                    self.Reader.currentFrequencyToggle = "SGI"
                    # self.freqToggleSet.on_next("SGI")
                    logging.info(f"Zero Point Set for reader {self.Reader.readerNumber}: {zeroPoint} MHz")
                    self.Reader.resetReaderRun()
                    self.createDisplayMenus()
                    self.finishedEquilibrationPeriod = True
        except:
            raise ZeroPointException(
                f"Failed to find the zero point for reader {self.Reader.readerNumber}, last 5 points: {self.Reader.getResultSet().getMaxFrequencySmooth()[-5:]}")

    def takeSweep(self):
        self.Reader.Indicator.changeIndicatorYellow()
        self.checkZeroPoint()
        sweepData = self.Reader.SibInterface.takeScan(
            self.Reader.FileManager.getCurrentScan(),
            self.disableFullSaveFiles,
        )
        self.Reader.getAnalyzer().analyzeScan(sweepData, self.denoiseSet)
        self.Reader.plotFrequencyButton.invoke()  # any changes to GUI must be in main_shared thread
        self.Reader.Analyzer.createAnalyzedFiles()
        # self.Reader.HarvestAlgorithm.check(self.Reader.getResultSet())
        self.Reader.Indicator.changeIndicatorGreen()
        if self.Reader.finishedEquilibrationPeriod:
            self.Reader.AwsService.uploadExperimentFilesOnInterval(
                self.Reader.FileManager.getCurrentScanNumber(),
                self.guidedSetupForm,
            )
        if self.Reader.readerNumber in self.currentIssues and not self.currentIssues[self.Reader.readerNumber].resolved:
            self.currentIssues[self.Reader.readerNumber].resolveIssue()
            if type(self.currentIssues[self.Reader.readerNumber]) is Issue:
                self.Reader.AutomatedIssueManager.updateIssue(self.currentIssues[self.Reader.readerNumber])
            del self.currentIssues[self.Reader.readerNumber]

    def mainLoop(self):
        if self.isDevMode:
            self.guidedSetupForm.scanRate = DevProperties().scanRate
        self.thread.shutdown_flag = threading.Event()

        while not self.thread.shutdown_flag.is_set():
            startTime = time.time()
            try:
                try:
                    self.takeSweep()
                except SIBConnectionError:
                    if self.Reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[self.Reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[self.Reader.readerNumber] = self.currentIssues[self.Reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[self.Reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveHardwareIssue,
                            f"Automated - Reader Connection Error On Reader {self.Reader.readerNumber}.",
                            self.Reader.AutomatedIssueManager.createIssue,
                        )
                    self.Reader.Indicator.changeIndicatorRed()
                    self.Reader.getAnalyzer().recordFailedScan()
                    logging.exception(
                        f'Connection Error: Reader {self.Reader.readerNumber} failed to take scan {self.Reader.FileManager.getCurrentScanNumber()}')
                    text_notification.setText(f"Sweep Failed, check reader {self.Reader.readerNumber} connection.")
                except SIBReconnectException:
                    if self.Reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[self.Reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[self.Reader.readerNumber] = self.currentIssues[self.Reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[self.Reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveHardwareIssue,
                            f"Automated - Hardware Issue Identified On Reader {self.Reader.readerNumber}.",
                            self.Reader.AutomatedIssueManager.createIssue,
                        )
                    self.Reader.Indicator.changeIndicatorRed()
                    self.Reader.getAnalyzer().recordFailedScan()
                    logging.exception(
                        f'Reader {self.Reader.readerNumber} failed to take scan {self.Reader.FileManager.getCurrentScanNumber()}, but reconnected successfully')
                    text_notification.setText(
                        f"Sweep failed for reader {self.Reader.readerNumber}, SIB reconnection was successful.")
                except SIBException:
                    if self.Reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[self.Reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[self.Reader.readerNumber] = self.currentIssues[self.Reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[self.Reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveHardwareIssue,
                            f"Automated - Hardware Issue Identified On Reader {self.Reader.readerNumber}.",
                            self.Reader.AutomatedIssueManager.createIssue,
                        )
                    self.Reader.Indicator.changeIndicatorRed()
                    self.Reader.getAnalyzer().recordFailedScan()
                    logging.exception(
                        f'Hardware Problem: Reader {self.Reader.readerNumber} failed to take scan {self.Reader.FileManager.getCurrentScanNumber()}')
                    text_notification.setText(
                        f"Sweep Failed With Hardware Cause for reader {self.Reader.readerNumber}, contact a Skroot representative if the issue persists.")
                except AnalysisException:
                    if self.Reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[self.Reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[self.Reader.readerNumber] = self.currentIssues[self.Reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[self.Reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveAnalysisIssue,
                            f"Automated - Analysis Failed On Reader {self.Reader.readerNumber}.",
                            self.Reader.AutomatedIssueManager.createIssue,
                        )
                    self.Reader.Indicator.changeIndicatorRed()
                    logging.exception(f'Error Analyzing Data, Reader {self.Reader.readerNumber} failed to analyze scan {self.Reader.FileManager.getCurrentScanNumber()}')
                    text_notification.setText(f"Sweep Analysis Failed, check sensor placement on reader {self.Reader.readerNumber}.")
                finally:
                    self.Timer.updateTime()
                    self.Reader.FileManager.incrementScanNumber(self.scanRate)
                if not self.issueOccurredFn():
                    text_notification.setText("All readers successfully recorded data.")
            except:
                logging.exception('Unknown error has occurred')
            finally:
                currentTime = time.time()
                self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
        text_notification.setText(f"Reader {self.Reader.readerNumber} finished run.", ('Courier', 9, 'bold'))
        if self.Reader.finishedEquilibrationPeriod:
            self.Reader.AwsService.uploadFinalExperimentFiles(self.guidedSetupForm)
        self.resetRunFunc(self.Reader.readerNumber)
        logging.info(f'Reader {self.Reader.readerNumber} finished run.')

    def checkIfScanTookTooLong(self, timeTaken):
        if timeTaken > self.scanRate * 60:
            self.scanRate = math.ceil(timeTaken / 60)
            text_notification.setText(f"Took too long to take scans. Scan rate now {self.scanRate}.")
            logging.info(f'{timeTaken} seconds to take ALL scans')
            logging.info(f"Took too long to take scans. Scan rate now {self.scanRate}.")

    def waitUntilNextScan(self, currentTime, startTime):
        while currentTime - startTime < self.scanRate * 60:
            if self.thread.shutdown_flag.is_set():
                logging.info('Cancelling data collection due to stop button pressed')
                break
            time.sleep(0.05)
            self.Timer.updateTime()
            currentTime = time.time()

    def createDisplayMenus(self):
        settingsMenuDisplay = self.RootManager.instantiateNewMenubarRibbon()
        settingsMenuDisplay.add_command(label="SGI", command=lambda: self.freqToggleSetting("SGI"))
        settingsMenuDisplay.add_command(label="Signal Check",
                                        command=lambda: self.freqToggleSetting("Signal Check"))
        self.RootManager.addMenubarCascade("Display", settingsMenuDisplay)

    def freqToggleSetting(self, toggle):
        self.freqToggleSet.on_next(toggle)
        logging.info(f'freqToggleSet changed to {toggle}')

