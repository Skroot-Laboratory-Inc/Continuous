import math
import os
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk

import matplotlib as mpl
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from zipfile import ZipFile

import logger
import text_notification
from buttons import ButtonFunctions
from colors import ColorCycler
from dev import DevMode
from pdf import generatePdf
from server import ServerFileShare
from settings import Settings
from setup import Setup
from software_update import SoftwareUpdate
from timer import RunningTimer

mpl.use('TkAgg')


class MainShared:
    def __init__(self, version, major_version, minor_version):
        self.root = tk.Tk()  # everything in the application comes after this
        self.readerPlotFrame = None
        self.scanFrequency = None
        self.foundPorts = False
        self.currentFrame = None
        self.summaryPlot = None
        self.summaryCanvas = None
        self.summaryFig = None
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
        try:
            self.desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            self.os = 'windows'
        except KeyError:
            self.desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
            self.os = 'linux'
        self.baseSavePath = self.desktop + "/data"
        if not os.path.exists(self.baseSavePath):
            os.mkdir(self.baseSavePath)
        logger.loggerSetup(f'{self.desktop}/Calibration/log.txt', version)
        self.version = f'{major_version}.{minor_version}'
        self.numReaders = None
        self.savePath = ''
        self.cellApp = False
        self.foamingApp = False
        self.freqToggleSet = "Signal Check"
        self.splineToggleSet = False
        self.denoiseSet = True
        self.currentlyScanning = False
        self.disableSaveFullFiles = False
        self.emailSetting = False
        self.awsTimeBetweenUploads = 30
        self.awsLastUploadTime = 0
        self.scanRate = 0.5
        self.startFreq = 40
        self.stopFreq = 250
        self.nPoints = 2000
        self.thread = threading.Thread(target=self.mainLoop, args=())
        self.threadStatus = ''
        self.royalBlue = 'RoyalBlue4'
        self.white = 'white'
        self.ports = []
        try:
            self.location = sys._MEIPASS
        except AttributeError:
            self.location = os.getcwd()
        self.createRoot()
        self.ColorCycler = ColorCycler()
        self.Timer = RunningTimer()
        self.Readers = []
        self.Settings = Settings(self)
        self.Setup = Setup(self.root, self.Settings, self)
        self.Buttons = ButtonFunctions(self, self.location, self.root)
        self.DevMode = DevMode()
        self.ServerFileShare = ServerFileShare(self)
        self.SoftwareUpdate = SoftwareUpdate(self.root, major_version, minor_version, self.location)
        self.isDevMode = self.DevMode.isDevMode

    def createRoot(self):
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        if self.os == 'windows':
            self.root.state('zoomed')
        elif self.os == 'linux':
            self.root.attributes('-zoomed', True)

        def _create_circle(this, x, y, r, **kwargs):
            return this.create_oval(x - r, y - r, x + r, y + r, **kwargs)

        tk.Canvas.create_circle = _create_circle

    def mainLoop(self):
        self.thread.shutdown_flag = threading.Event()
        while not self.thread.shutdown_flag.is_set():
            startTime = time.time()
            try:
                for Reader in self.Readers:
                    try:
                        if not self.isDevMode:
                            self.scanFrequency, self.scanMagnitude, self.scanPhase, success = Reader.ReaderInterface.takeScan(
                                f'{Reader.savePath}/{Reader.scanNumber}.csv')
                            if not success:
                                continue
                            Reader.analyzeScan(f'{Reader.savePath}/{Reader.scanNumber}.csv')
                        else:
                            Reader.addDevPoint()
                        if self.denoiseSet:
                            Reader.denoiseResults()
                        Reader.plotFrequencyButton.invoke()  # any changes to GUI must be in main thread
                        Reader.createAnalyzedFiles()
                        if not self.ServerFileShare.disabled:
                            Reader.createServerJsonFile()
                            Reader.sendFilesToServer()
                        if self.disableSaveFullFiles:
                            deleteScanFile(f'{Reader.savePath}/{Reader.scanNumber}.csv')
                        Reader.printScanFreq()
                        Reader.checkFoaming()
                        # Reader.checkContamination()
                        Reader.checkHarvest()
                    except:
                        logger.exception(f'Unchecked error, Reader {Reader.readerNumber} failed to take scan')
                    finally:
                        self.Timer.updateTime()
                        incrementScan(Reader)
                self.summaryPlotButton.invoke()  # any changes to GUI must be in main thread
                generatePdf(self.savePath, self.Readers)
                self.awsUploadPdfFile()
            except:
                logger.exception('Unknown error has occurred')
            finally:
                currentTime = time.time()
                self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
        text_notification.setText("Stopped.", ('Courier', 9, 'bold'), self.royalBlue, self.white)
        self.resetRun()
        logger.info('Stopped scanning')

    def awsCheckSoftwareUpdates(self):
        if not self.DevMode.isDevMode:
            newestVersion, updateRequired = self.SoftwareUpdate.checkForSoftwareUpdates()
            if updateRequired:
                text_notification.setText(
                    f"Newer software available v{newestVersion} consider upgrading to use new features")

    def downloadSoftwareUpdate(self):
        try:
            downloadUpdate = self.SoftwareUpdate.downloadSoftwareUpdate(fr'{os.path.dirname(self.location)}/DesktopApp.zip')
            if downloadUpdate:
                with ZipFile(fr'{os.path.dirname(self.location)}/DesktopApp.zip', 'r') as file:
                    file.extractall()
                if self.os == "linux":
                    shutil.copyfile(rf'{self.location}/resources/desktopApp.desktop',
                                    rf'{os.path.dirname(self.location)}/share/applications/desktopApp.desktop')
                    process = subprocess.Popen([f'{self.location}/resources/scripts/install-script.sh'])
                    text_notification.setText("Installing new dependencies... please wait. This may take up to a minute.")
                    process.wait()
                text_notification.setText(
                    f"New software version updated v{self.SoftwareUpdate.newestMajorVersion}.{self.SoftwareUpdate.newestMinorVersion}")
            else:
                text_notification.setText("Software update aborted.")
        except:
            logger.exception("failed to update software")

    def awsUploadPdfFile(self):
        if not self.DevMode.isDevMode and not self.SoftwareUpdate.disabled:
            if self.SoftwareUpdate.dstPdfName is None:
                self.SoftwareUpdate.findFolderAndUploadFile(f'{self.savePath}/Summary.pdf', "application/pdf")
            else:
                if (self.Readers[0].scanNumber - self.awsLastUploadTime) > self.awsTimeBetweenUploads:
                    self.SoftwareUpdate.uploadFile(f'{self.savePath}/Summary.pdf', self.SoftwareUpdate.dstPdfName, 'application/pdf')
                    self.awsLastUploadTime = self.Readers[0].scanNumber

    def awsUploadLogFile(self):
        if not self.DevMode.isDevMode and not self.SoftwareUpdate.disabled:
            self.SoftwareUpdate.uploadFile(f'{self.desktop}/Calibration/log.txt', self.SoftwareUpdate.dstLogName, 'text/plain')
            text_notification.setText("Log sent to Skroot, please contact a representative with more context.")
            return True
        return False

    def checkIfScanTookTooLong(self, timeTaken):
        if timeTaken > self.scanRate * 60:
            for Reader in self.Readers:
                Reader.scanRate = math.ceil(timeTaken / 60)
            self.scanRate = math.ceil(timeTaken / 60)
            text_notification.setText(f"Took too long to take scans \nScan rate now {self.Readers[0].scanRate}.")
            logger.info(f'{timeTaken} seconds to take ALL scans')
            logger.info(f"Took too long to take scans \nScan rate now {self.Readers[0].scanRate}.")

    def waitUntilNextScan(self, currentTime, startTime):
        while currentTime - startTime < self.scanRate * 60:
            if self.thread.shutdown_flag.is_set():
                logger.info('Cancelling data collection due to stop button pressed')
                break
            time.sleep(0.05)
            self.Timer.updateTime()
            currentTime = time.time()

    def plotSummary(self):
        try:
            try:
                self.summaryFig.clear()
            except AttributeError:
                size = 3
                self.summaryFig = Figure(figsize=(size, size))
                self.summaryFig.set_tight_layout(True)
            self.summaryPlot = self.summaryFig.add_subplot(111)
            self.summaryPlot.tick_params(axis='both', which='minor', labelsize=7)
            self.summaryPlot.tick_params(axis='both', which='major', labelsize=7)
            self.ColorCycler.reset()

            if self.freqToggleSet == "SGI" or self.freqToggleSet == "Signal Check":
                self.summaryPlot.set_ylabel('Skroot Growth Index (SGI)', fontsize=9)
                self.summaryPlot.set_title(f'Summary', fontsize=9)
                for Reader in self.Readers:
                    readerColor = self.ColorCycler.getNext()
                    if self.denoiseSet:
                        y = Reader.frequencyToIndex(Reader.denoiseFrequencySmooth)
                        self.summaryPlot.scatter(Reader.denoiseTimeSmooth, y, s=20, color=readerColor)
                    else:
                        y = Reader.frequencyToIndex(Reader.minFrequencySmooth)
                        self.summaryPlot.scatter(Reader.time, y, s=20, color=readerColor)
                    if self.freqToggleSet == "SGI":
                        self.summaryPlot.set_xlim([Reader.inoculatedTime, None])
            elif self.freqToggleSet == "Signal Strength":
                self.summaryPlot.set_ylabel('Change in Signal Strength (dB)', fontsize=9)
                self.summaryPlot.set_title(f'Summary', fontsize=9)
                for Reader in self.Readers:
                    readerColor = self.ColorCycler.getNext()
                    if self.denoiseSet:
                        y = [yval - Reader.denoiseTotalMinSmooth[0] for yval in Reader.denoiseTotalMinSmooth]
                        self.summaryPlot.scatter(Reader.denoiseTimedBSmooth, y, s=20, color=readerColor)
                    else:
                        y = [yval - Reader.minDb[0] for yval in Reader.minDbSmooth]
                        self.summaryPlot.scatter(Reader.time, y, s=20, color=readerColor)
            self.summaryPlot.set_xlabel('Time (hours)', fontsize=7)
            self.summaryFig.savefig(f'{self.savePath}/Summary Figure.jpg', dpi=500)
            try:
                self.summaryCanvas.get_tk_widget().pack()
            except AttributeError:
                self.summaryCanvas = FigureCanvasTkAgg(self.summaryFig, master=self.summaryFrame)
            except:
                self.summaryCanvas = FigureCanvasTkAgg(self.summaryFig, master=self.summaryFrame)
            self.summaryCanvas.draw()
            self.summaryCanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except:
            logger.exception("Failed to generate summaryPlot")

    def onClosing(self):
        if tk.messagebox.askokcancel("Exit", "Are you sure you want to close the program?"):
            self.root.destroy()

    def resetRun(self):
        for Reader in self.Readers:
            try:
                Reader.ReaderInterface.close()
            except AttributeError:
                Reader.socket = None
                logger.exception(f'Failed to close Reader {Reader.readerNumber} socket')
        for widgets in self.readerPlotFrame.winfo_children():
            widgets.destroy()
        versionLabel = tk.Label(self.readerPlotFrame, text=f'Version: v{self.version}', bg='white')
        versionLabel.place(relx=0.0, rely=1.0, anchor='sw')
        self.thread = threading.Thread(target=self.mainLoop, args=())
        self.foundPorts = False
        self.ports = []
        self.Buttons.ReaderInterfaces = []
        self.Readers = []
        self.Buttons.guidedSetupButton.invoke()

    def showFrame(self, frame):
        self.currentFrame = frame
        try:
            frame.place(relx=0, rely=0.05, relwidth=1, relheight=0.9)
            frame.tkraise()
        except:
            logger.exception('Failed to change the frame visible')
        self.summaryFrame.tkraise()


def incrementScan(Reader):
    Reader.scanNumber += Reader.scanRate


def deleteScanFile(filename):
    os.remove(filename)
