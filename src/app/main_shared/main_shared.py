import csv
import logging
import math
import os
import shutil
import stat
import subprocess
import threading
import time
import tkinter as tk
from importlib.metadata import version as version_api
from zipfile import ZipFile

import numpy as np
from reactivex.subject import BehaviorSubject
from sibcontrol import SIBException, SIBConnectionError

from src.app.exception.analysis_exception import AnalysisException, ZeroPointException
from src.app.exception.sib_exception import SIBReconnectException
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper import helper_functions
from src.app.helper.helper_functions import frequencyToIndex, getOperatingSystem
from src.app.initialization.buttons import ButtonFunctions
from src.app.initialization.settings import Settings
from src.app.initialization.setup import Setup
from src.app.initialization.software_update import SoftwareUpdate
from src.app.main_shared.end_of_experiment_view import EndOfExperimentView
from src.app.properties.dev_properties import DevProperties
from src.app.properties.properties import CommonProperties
from src.app.sib.port_allocator import PortAllocator
from src.app.theme.color_cycler import ColorCycler
from src.app.theme.colors import Colors
from src.app.widget import logger, text_notification
from src.app.widget.figure import FigureCanvas
from src.app.widget.pdf import generatePdf
from src.app.widget.timer import RunningTimer


class MainShared:
    def __init__(self, version, major_version, minor_version):
        self.root = tk.Tk()  # everything in the application comes after this
        self.GlobalFileManager = None
        self.readerPlotFrame = None
        self.foundPorts = False
        self.currentFrame = None
        self.summaryPlotButton = None
        self.summaryFrame = None
        self.submitButton = None
        self.waterFreqInput = None
        self.stopButton = None
        self.startButton = None
        self.airFreqInput = None
        self.menubar = None
        self.cellType = None
        self.year = None
        self.day = None
        self.month = None
        self.Properties = CommonProperties()
        self.CommonFileManager = CommonFileManager()
        self.Colors = Colors()
        self.awsTimeBetweenUploads = self.Properties.awsTimeBetweenUploads
        self.startFreq = self.Properties.defaultStartFrequency
        self.stopFreq = self.Properties.defaultEndFrequency
        logger.loggerSetup(self.CommonFileManager.getExperimentLog(), version)
        logging.info(f'Sibcontrol version: {version_api("sibcontrol")}')
        self.version = f'{major_version}.{minor_version}'
        self.numReaders = 0
        self.savePath = ''
        self.freqToggleSet = BehaviorSubject("Signal Check")
        self.denoiseSet = True
        self.disableSaveFullFiles = False
        self.awsLastUploadTime = 0
        self.scanRate = 0
        self.thread = threading.Thread(target=self.mainLoop, args=(), daemon=True)
        self.threadStatus = ''
        self.primaryColor = self.Colors.primaryColor
        self.secondaryColor = self.Colors.secondaryColor
        self.PortAllocator = PortAllocator()
        self.finishedEquilibrationPeriod = False
        self.createRoot()
        self.ColorCycler = ColorCycler()
        self.Timer = RunningTimer()
        self.Readers = []
        self.Settings = Settings(self)
        self.Setup = Setup(self.root, self.Settings, self)
        self.Buttons = ButtonFunctions(self, self.root, self.PortAllocator)
        self.DevProperties = DevProperties()
        self.SoftwareUpdate = SoftwareUpdate(self.root, major_version, minor_version)
        self.isDevMode = self.DevProperties.isDevMode
        self.SummaryFigureCanvas = FigureCanvas(
            'k',
            'Skroot Growth Index (SGI)',
            'Time (hrs)',
            self.secondaryColor,
            'Summary',
            '',
            7,
            9
        )

    def createRoot(self):
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        operatingSystem = getOperatingSystem()
        if operatingSystem == 'windows':
            self.root.state('zoomed')
        elif operatingSystem == 'linux':
            self.root.attributes('-zoomed', True)

        def _create_circle(this, x, y, r, **kwargs):
            return this.create_oval(x - r, y - r, x + r, y + r, **kwargs)

        tk.Canvas.create_circle = _create_circle

    def mainLoop(self):
        self.thread.shutdown_flag = threading.Event()
        while not self.thread.shutdown_flag.is_set():
            errorOccurredWhileTakingScans = False
            startTime = time.time()
            try:
                for Reader in self.Readers:
                    try:
                        if not self.isDevMode:
                            Reader.Indicator.changeIndicatorYellow()
                            sweepData = Reader.ReaderInterface.takeScan(Reader.FileManager.getCurrentScan(),
                                                                        self.disableSaveFullFiles)
                            Reader.getAnalyzer().analyzeScan(sweepData, self.denoiseSet)
                        else:
                            Reader.addDevPoint()
                        try:
                            if Reader.getResultSet().getTime()[-1] >= self.equilibrationTime and Reader.getZeroPoint() == 1:
                                if self.equilibrationTime == 0 and Reader.getResultSet().getMaxFrequencySmooth()[
                                    -1] != np.nan:
                                    zeroPoint = Reader.getResultSet().getMaxFrequencySmooth()[-1]
                                elif self.equilibrationTime == 0 and Reader.getResultSet().getMaxFrequencySmooth()[
                                    -1] == np.nan:
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
                        Reader.recordFailedScan()
                        logging.exception(
                            f'Connection Error: Reader {Reader.readerNumber} failed to take scan {Reader.FileManager.getCurrentScanNumber()}')
                        text_notification.setText(f"Sweep Failed, check reader {Reader.readerNumber} connection.")
                    except SIBReconnectException:
                        errorOccurredWhileTakingScans = True
                        Reader.Indicator.changeIndicatorRed()
                        Reader.recordFailedScan()
                        logging.exception(
                            f'Reader {Reader.readerNumber} failed to take scan {Reader.FileManager.getCurrentScanNumber()}, but reconnected successfully')
                        text_notification.setText(
                            f"Sweep failed for reader {Reader.readerNumber}, SIB reconnection was successful.")
                    except SIBException:
                        errorOccurredWhileTakingScans = True
                        Reader.Indicator.changeIndicatorRed()
                        Reader.recordFailedScan()
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
                        Reader.FileManager.incrementScanNumber(Reader.scanRate)
                if self.finishedEquilibrationPeriod:
                    self.createSummaryAnalyzedFile()
                    self.summaryPlotButton.invoke()  # any changes to GUI must be in main_shared thread
                    generatePdf(self.Readers,
                                self.GlobalFileManager.getSetupForm(),
                                self.GlobalFileManager.getSummaryFigure(),
                                self.GlobalFileManager.getSummaryPdf())
                    self.awsUploadPdfFile()
                if not errorOccurredWhileTakingScans:
                    text_notification.setText("All readers successfully recorded data.")
            except:
                logging.exception('Unknown error has occurred')
            finally:
                currentTime = time.time()
                self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
        text_notification.setText("Experiment Ended.", ('Courier', 9, 'bold'), self.primaryColor, self.secondaryColor)
        self.resetRun()
        logging.info('Experiment Ended')

    def awsCheckSoftwareUpdates(self):
        if not self.DevProperties.isDevMode:
            newestVersion, updateRequired = self.SoftwareUpdate.checkForSoftwareUpdates()
            if updateRequired:
                text_notification.setText(
                    f"Newer software available v{newestVersion} consider upgrading to use new features")

    def downloadSoftwareUpdate(self):
        try:
            downloadUpdate = self.SoftwareUpdate.downloadSoftwareUpdate(self.CommonFileManager.getTempUpdateFile())
            if downloadUpdate:
                with ZipFile(self.CommonFileManager.getTempUpdateFile(), 'r') as file:
                    file.extractall()
                if getOperatingSystem() == "linux":
                    shutil.copyfile(self.CommonFileManager.getLocalDesktopFile(),
                                    self.CommonFileManager.getRemoteDesktopFile())
                    text_notification.setText(
                        "Installing new dependencies... please wait. This may take up to a minute.")
                    helper_functions.runShScript(self.CommonFileManager.getInstallScript(),
                                                 self.CommonFileManager.getExperimentLog())
                text_notification.setText(
                    f"New software version updated v{self.SoftwareUpdate.newestMajorVersion}.{self.SoftwareUpdate.newestMinorVersion}")
            else:
                text_notification.setText("Software update aborted.")
        except:
            logging.exception("failed to update software")

    def awsUploadPdfFile(self):
        if not self.DevProperties.isDevMode and not self.SoftwareUpdate.disabled:
            if self.SoftwareUpdate.dstPdfName is None:
                self.SoftwareUpdate.findFolderAndUploadFile(self.GlobalFileManager.getSummaryPdf(), "application/pdf")
            else:
                if (self.Readers[
                        0].FileManager.getCurrentScanNumber() - self.awsLastUploadTime) > self.awsTimeBetweenUploads:
                    self.SoftwareUpdate.uploadFile(self.GlobalFileManager.getSummaryPdf(),
                                                   self.SoftwareUpdate.dstPdfName,
                                                   'application/pdf')
                    self.awsLastUploadTime = self.Readers[0].FileManager.getCurrentScanNumber()

    def awsUploadLogFile(self):
        if not self.DevProperties.isDevMode and not self.SoftwareUpdate.disabled:
            self.SoftwareUpdate.uploadFile(self.CommonFileManager.getExperimentLog(), self.SoftwareUpdate.dstLogName,
                                           'text/plain')
            return True
        return False

    def checkIfScanTookTooLong(self, timeTaken):
        if timeTaken > self.scanRate * 60:
            for Reader in self.Readers:
                Reader.scanRate = math.ceil(timeTaken / 60)
            self.scanRate = math.ceil(timeTaken / 60)
            text_notification.setText(f"Took too long to take scans \nScan rate now {self.Readers[0].scanRate}.")
            logging.info(f'{timeTaken} seconds to take ALL scans')
            logging.info(f"Took too long to take scans \nScan rate now {self.Readers[0].scanRate}.")

    def waitUntilNextScan(self, currentTime, startTime):
        while currentTime - startTime < self.scanRate * 60:
            if self.thread.shutdown_flag.is_set():
                logging.info('Cancelling data collection due to stop button pressed')
                break
            time.sleep(0.05)
            self.Timer.updateTime()
            currentTime = time.time()

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

    def onClosing(self):
        if tk.messagebox.askokcancel("Exit", "Are you sure you want to close the program?"):
            self.copyFilesToDebuggingFolder(self.Readers)
            self.copyFilesToAnalysisFolder(self.Readers)
            self.root.destroy()

    def resetRun(self):
        for widgets in self.readerPlotFrame.winfo_children():
            widgets.destroy()
        for Reader in self.Readers:
            try:
                Reader.ReaderInterface.close()
            except AttributeError:
                Reader.socket = None
                logging.exception(f'Failed to close Reader {Reader.readerNumber} socket')
        self.copyFilesToDebuggingFolder(self.Readers)
        self.copyFilesToAnalysisFolder(self.Readers)
        self.PortAllocator.resetPorts()
        self.freqToggleSet.on_completed()
        self.freqToggleSet = BehaviorSubject("Signal Check")
        self.thread = threading.Thread(target=self.mainLoop, args=(), daemon=True)
        self.foundPorts = False
        self.Buttons.ReaderInterfaces = []
        self.Readers = []
        if self.finishedEquilibrationPeriod:
            endOfExperimentView = EndOfExperimentView(self.root, self.GlobalFileManager)
            endOfExperimentFrame = endOfExperimentView.createEndOfExperimentView()
            self.Buttons.createGuidedSetupButton(endOfExperimentFrame)
            self.Buttons.guidedSetupButton.grid(row=2, column=1, sticky='se', padx=10, pady=10)
            self.SummaryFigureCanvas.frequencyCanvas = None
            self.endOfExperimentFrame = endOfExperimentFrame
        else:
            self.Buttons.createGuidedSetupButton(self.readerPlotFrame)
            self.Buttons.guidedSetupButton.invoke()
        self.finishedEquilibrationPeriod = False

    def copyFilesToDebuggingFolder(self, Readers):
        logSubdir = f'{self.GlobalFileManager.getSavePath()}/Log'
        if not os.path.exists(logSubdir):
            os.mkdir(logSubdir)
        filesToCopy = {self.CommonFileManager.getExperimentLog(): 'Experiment Log.txt'}
        for Reader in Readers:
            filesToCopy[
                Reader.FileManager.getCalibrationLocalLocation()] = f'Calibration_{Reader.readerNumber}.csv'
        for currentFileLocation, newFileLocation in filesToCopy.items():
            if os.path.exists(currentFileLocation):
                shutil.copy(currentFileLocation, f'{logSubdir}/{newFileLocation}')

    def copyFilesToAnalysisFolder(self, Readers):
        analysisSubdir = f'{self.GlobalFileManager.getSavePath()}/Analysis'
        if not os.path.exists(analysisSubdir):
            os.mkdir(analysisSubdir)
        filesToCopy = {
            self.GlobalFileManager.getSummaryAnalyzed(): 'Experiment Summary.csv',
            self.GlobalFileManager.getSummaryPdf(): 'Experiment Summary.pdf',
            self.GlobalFileManager.getSetupForm(): 'Setup Form.png',
            self.CommonFileManager.getReadme(): 'README.md',
        }
        for Reader in Readers:
            filesToCopy[Reader.FileManager.getSecondAxis()] = f'Reader {Reader.readerNumber} Second Axis.csv'
            filesToCopy[Reader.FileManager.getExperimentNotes()] = f'Reader {Reader.readerNumber} Experiment Notes.txt'
        for currentFileLocation, newFileLocation in filesToCopy.items():
            if os.path.exists(currentFileLocation):
                shutil.copy(currentFileLocation, f'{analysisSubdir}/{newFileLocation}')

    def showFrame(self, frame):
        self.currentFrame = frame
        try:
            frame.place(relx=0, rely=0.05, relwidth=1, relheight=0.9)
            frame.tkraise()
        except:
            logging.exception('Failed to change the frame visible')
        self.summaryFrame.tkraise()
