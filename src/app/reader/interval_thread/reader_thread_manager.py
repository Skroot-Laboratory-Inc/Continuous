import logging
import math
import os
import threading
import time
from typing import Callable

import numpy as np

from src.app.helper_methods.custom_exceptions.analysis_exception import ZeroPointException, AnalysisException, \
    SensorNotFoundException
from src.app.helper_methods.custom_exceptions.sib_exception import SIBReconnectException
from src.app.helper_methods.data_helpers import frequencyToIndex
from src.app.helper_methods.helper_functions import getZeroPoint, createScanFile, copyExperimentLog
from src.app.helper_methods.model.issue.issue import Issue
from src.app.helper_methods.model.issue.potential_issue import PotentialIssue
from src.app.helper_methods.model.setup_reader_form_input import SetupReaderFormInput
from src.app.properties.common_properties import CommonProperties
from src.app.properties.dev_properties import DevProperties
from src.app.properties.issue_properties import IssueProperties
from src.app.reader.reader import Reader
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification
from src.app.widget.sidebar.configurations.secondary_axis_type import SecondaryAxisType
from src.app.widget.sidebar.configurations.secondary_axis_units import SecondaryAxisUnits
from src.resources.sibcontrol.sibcontrol import SIBException, SIBConnectionError


class ReaderThreadManager:
    def __init__(self, reader: Reader, rootManager: RootManager, guidedSetupForm: SetupReaderFormInput,
                 resetRunFunc, issueOccurredFn: Callable):
        self.guidedSetupForm = guidedSetupForm
        self.issueOccurredFn = issueOccurredFn
        self.scanRate = guidedSetupForm.getScanRate()
        self.equilibrationTime = guidedSetupForm.getEquilibrationTime()
        self.thread = threading.Thread(target=self.mainLoop, args=(reader,), daemon=True)
        self.Timer = reader.ReaderPage.getTimer()
        self.isDevMode = DevProperties().isDevMode
        self.RootManager = rootManager
        self.Reader = reader
        self.kpiForm = self.Reader.ReaderPage.getReaderFrame().kpiForm
        self.kpiForm.lastSecondAxisEntry.subscribe(lambda value: threading.Thread(
            target=self.addSecondaryAxisValue,
            args=(float(value),)
        ).start())
        # Current Issues is supposed to be a dict of all issues used for updating text_notification on successful runs.
        # Needs fixing.
        self.currentIssues = {}

        self.finishedEquilibrationPeriod = False
        self.disableFullSaveFiles = CommonProperties().disableSaveFullFiles
        self.denoiseSet = CommonProperties().denoiseSet

        self.resetRunFunc = resetRunFunc

    def addSecondaryAxisValue(self, value: float):
        self.Reader.SecondaryAxisTracker.addValue(value)
        self.Reader.AwsService.uploadSecondAxis()
        text_notification.setText(f"Added {SecondaryAxisType().getConfig()} of {value} {SecondaryAxisUnits().getAsUnit()}")

    def startReaderLoop(self, user: str):
        self.kpiForm.setConstants(self.guidedSetupForm.getLotId(), user)
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
                        text_notification.setText("Failed to set zero point. SGI values unreliable.")
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
        analyzer = self.Reader.getAnalyzer()
        resultSet = self.Reader.getResultSet()
        harvestAlgorithm = self.Reader.HarvestAlgorithm
        try:
            reader.FileManager.updateScanName()
            reader.Indicator.changeIndicatorYellow()
            self.checkZeroPoint()
            sweepData = reader.SibInterface.takeScan(
                os.path.splitext(reader.FileManager.getCurrentScan())[0],
                resultSet.getCurrentVolts(),
            )
            createScanFile(reader.FileManager.getCurrentScan(), sweepData)
            analyzer.analyzeScan(sweepData, self.denoiseSet)
            reader.SibInterface.setReferenceFrequency(resultSet.getCurrentFrequency())
            reader.plotFrequencyButton.invoke()  # any changes to GUI must be in common_modules thread
            harvestAlgorithm.check(resultSet)
            if harvestAlgorithm.currentHarvestPrediction != 0 and not np.isnan(harvestAlgorithm.currentHarvestPrediction):
                self.kpiForm.saturationDate = harvestAlgorithm.currentHarvestPrediction
            if reader.finishedEquilibrationPeriod:
                self.kpiForm.sgi = frequencyToIndex(analyzer.zeroPoint, resultSet.getDenoiseFrequencySmooth())[-1]
            reader.Indicator.changeIndicatorGreen()
            if reader.readerNumber in self.currentIssues and not self.currentIssues[reader.readerNumber].resolved:
                self.currentIssues[reader.readerNumber].resolveIssue()
                if type(self.currentIssues[reader.readerNumber]) is Issue:
                    reader.AutomatedIssueManager.updateIssue(self.currentIssues[reader.readerNumber])
                del self.currentIssues[reader.readerNumber]
        finally:
            analyzer.createAnalyzedFiles()
            if reader.finishedEquilibrationPeriod:
                reader.AwsService.uploadExperimentFilesOnInterval(
                    reader.FileManager.getCurrentScanDate(),
                    self.guidedSetupForm.getLotId(),
                    self.kpiForm.saturationDate,
                    reader.AutomatedIssueManager.hasOpenIssues(),
                    resultSet.getStartTime(),
                    self.guidedSetupForm.getWarehouse(),
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
                        f'Connection Error: Failed to take scan {reader.FileManager.getCurrentScanDate()}',
                        extra={"id": f"Reader {reader.readerNumber}"})
                    text_notification.setText(f"Reader hardware disconnected.\nPlease contact your system administrator.  ")
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
                        f'Failed to take scan {reader.FileManager.getCurrentScanDate()}, but reconnected successfully',
                        extra={"id": f"Reader {reader.readerNumber}"})
                    text_notification.setText(
                        'Sweep failed, but connection re-established. No further action is necessary.',
                    )
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
                        f'Hardware Problem: Failed to take scan {reader.FileManager.getCurrentScanDate()}',
                        extra={"id": f"Reader {reader.readerNumber}"})
                    text_notification.setText(
                        f"Reader hardware disconnected.\nPlease contact your system administrator. ")
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
                        f'Error Analyzing Data, failed to analyze scan {reader.FileManager.getCurrentScanDate()}',
                        extra={"id": f"Reader {reader.readerNumber}"})
                    text_notification.setText(
                        f"Sweep analysis failed, check vessel placement.")
                except SensorNotFoundException as e:
                    if reader.readerNumber in self.currentIssues:
                        if type(self.currentIssues[reader.readerNumber]) is PotentialIssue:
                            self.currentIssues[reader.readerNumber] = self.currentIssues[
                                reader.readerNumber].persistIssue()
                    else:
                        self.currentIssues[reader.readerNumber] = PotentialIssue(
                            IssueProperties().consecutiveAnalysisIssue,
                            f"Automated - Sensor not found on Reader {reader.readerNumber}.",
                            reader.AutomatedIssueManager.createIssue,
                        )
                    reader.Indicator.changeIndicatorRed()
                    text_notification.setText(f"Sensor not found above Reader Port {reader.readerNumber}.")
                    logging.info(e.message, extra={"id": f"Reader {reader.readerNumber}"})
                finally:
                    self.Timer.updateTime()
                if not self.issueOccurredFn():
                    text_notification.setText("Reader has recorded a sweep.")
            except:
                logging.exception('Unknown error has occurred', extra={"id": f"Reader {reader.readerNumber}"})
            finally:
                currentTime = time.time()
                if self.isDevMode and DevProperties().enforceScanRate:
                    pass
                else:
                    self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
        text_notification.setText("Run Finished.")
        if reader.finishedEquilibrationPeriod:
            reader.AwsService.uploadFinalExperimentFiles(
                self.guidedSetupForm.getLotId(),
                self.kpiForm.saturationDate,
                self.Reader.getAnalyzer().ResultSet.getStartTime(),
                self.guidedSetupForm.getWarehouse(),
            )
        self.resetRunFunc(reader.readerNumber)
        copyExperimentLog(self.Reader.FileManager.getReaderSavePath())
        logging.info(f'Finished run.', extra={"id": f"Reader {reader.readerNumber}"})

    def checkIfScanTookTooLong(self, timeTaken):
        if timeTaken > self.scanRate * 60:
            self.scanRate = math.ceil(timeTaken / 60)
            text_notification.setText(f"Current scan rate is infeasible, updated to {self.scanRate}.")
            logging.info(f'{timeTaken} seconds to take scan. Scan rate now {self.scanRate}.',
                         extra={"id": f"Reader {self.Reader.readerNumber}"})

    def waitUntilNextScan(self, currentTime, startTime):
        # Wait removed for power consumption testing - scan immediately
        time.sleep(0.1)
        # while currentTime - startTime < self.scanRate * 60:
        #     if self.thread.shutdown_flag.is_set():
        #         logging.info('Cancelling data collection due to stop button pressed',
        #                      extra={"id": f"Reader {self.Reader.readerNumber}"})
        #         break
        #     time.sleep(0.05)
        #     self.Timer.updateTime()
        #     currentTime = time.time()
        pass
