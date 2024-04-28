import csv
import logging
import math
import os
import shutil
import stat
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
from zipfile import ZipFile

import matplotlib as mpl
from importlib.metadata import version as version_api
import numpy as np
from PIL import ImageTk, Image

import helper_functions
import logger
import text_notification
from buttons import ButtonFunctions
from colors import ColorCycler
from dev import DevMode
from figure import FigureCanvas
from helper_functions import frequencyToIndex
from pdf import generatePdf
from port_allocator import PortAllocator
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
        logging.info(f'Sibcontrol version: {version_api("sibcontrol")}')
        self.version = f'{major_version}.{minor_version}'
        self.numReaders = None
        self.savePath = ''
        self.cellApp = False
        self.foamingApp = False
        self.freqToggleSet = "Signal Check"
        self.denoiseSet = True
        self.disableSaveFullFiles = False
        self.emailSetting = False
        self.awsTimeBetweenUploads = 30
        self.awsLastUploadTime = 0
        self.scanRate = 0.5
        self.startFreq = 115
        self.stopFreq = 165
        self.thread = threading.Thread(target=self.mainLoop, args=())
        self.threadStatus = ''
        self.royalBlue = 'RoyalBlue4'
        self.white = 'white'
        self.PortAllocator = PortAllocator(self.os)
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
        self.Buttons = ButtonFunctions(self, self.location, self.root, self.PortAllocator)
        self.DevMode = DevMode()
        self.ServerFileShare = ServerFileShare(self)
        self.SoftwareUpdate = SoftwareUpdate(self.root, major_version, minor_version, self.location)
        self.isDevMode = self.DevMode.isDevMode
        self.SummaryFigureCanvas = FigureCanvas(
            'k',
            'Skroot Growth Index (SGI)',
            'Time (hrs)',
            self.white,
            'Summary',
            '',
            7,
            9
        )

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
                            Reader.analyzeScan(f'{Reader.savePath}/{Reader.scanNumber}.csv')
                            if not success:
                                continue
                        else:
                            Reader.addDevPoint()
                        if Reader.time[-1] >= self.equilibrationTime and Reader.zeroPoint == 1:
                            self.freqToggleSet = "SGI"
                            Reader.setZeroPoint(np.nanmean(Reader.minFrequencySmooth[-5:]))
                            Reader.resetReaderRun()
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
                        logging.exception(f'Unchecked error, Reader {Reader.readerNumber} failed to take scan')
                    finally:
                        self.Timer.updateTime()
                        incrementScan(Reader)
                if self.freqToggleSet == "SGI":
                    self.createSummaryAnalyzedFile()
                    self.summaryPlotButton.invoke()  # any changes to GUI must be in main thread
                    generatePdf(self.savePath, self.Readers)
                    self.awsUploadPdfFile()
            except:
                logging.exception('Unknown error has occurred')
            finally:
                currentTime = time.time()
                self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
        text_notification.setText("Stopped.", ('Courier', 9, 'bold'), self.royalBlue, self.white)
        self.resetRun()
        logging.info('Stopped scanning')

    def awsCheckSoftwareUpdates(self):
        if not self.DevMode.isDevMode:
            newestVersion, updateRequired = self.SoftwareUpdate.checkForSoftwareUpdates()
            if updateRequired:
                text_notification.setText(
                    f"Newer software available v{newestVersion} consider upgrading to use new features")

    def downloadSoftwareUpdate(self):
        try:
            downloadUpdate = self.SoftwareUpdate.downloadSoftwareUpdate(
                fr'{os.path.dirname(self.location)}/DesktopApp.zip')
            if downloadUpdate:
                with ZipFile(fr'{os.path.dirname(self.location)}/DesktopApp.zip', 'r') as file:
                    file.extractall()
                if self.os == "linux":
                    shutil.copyfile(rf'{self.location}/resources/desktopApp.desktop',
                                    rf'{os.path.dirname(self.location)}/share/applications/desktopApp.desktop')
                    text_notification.setText(
                        "Installing new dependencies... please wait. This may take up to a minute.")
                    runShScript(f'{self.location}/resources/scripts/install-script.sh', self.desktop)
                text_notification.setText(
                    f"New software version updated v{self.SoftwareUpdate.newestMajorVersion}.{self.SoftwareUpdate.newestMinorVersion}")
            else:
                text_notification.setText("Software update aborted.")
        except:
            logging.exception("failed to update software")

    def awsUploadPdfFile(self):
        if not self.DevMode.isDevMode and not self.SoftwareUpdate.disabled:
            if self.SoftwareUpdate.dstPdfName is None:
                self.SoftwareUpdate.findFolderAndUploadFile(f'{self.savePath}/Summary.pdf', "application/pdf")
            else:
                if (self.Readers[0].scanNumber - self.awsLastUploadTime) > self.awsTimeBetweenUploads:
                    self.SoftwareUpdate.uploadFile(f'{self.savePath}/Summary.pdf', self.SoftwareUpdate.dstPdfName,
                                                   'application/pdf')
                    self.awsLastUploadTime = self.Readers[0].scanNumber

    def awsUploadLogFile(self):
        if not self.DevMode.isDevMode and not self.SoftwareUpdate.disabled:
            self.SoftwareUpdate.uploadFile(f'{self.desktop}/Calibration/log.txt', self.SoftwareUpdate.dstLogName,
                                           'text/plain')
            text_notification.setText("Log sent to Skroot, please contact a representative with more context.")
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
                readerColor = self.ColorCycler.getNext()
                if self.denoiseSet:
                    yPlot = frequencyToIndex(Reader.zeroPoint, Reader.denoiseFrequencySmooth)
                    self.SummaryFigureCanvas.scatter(Reader.denoiseTimeSmooth, yPlot, 20, readerColor)
                else:
                    yPlot = frequencyToIndex(Reader.zeroPoint, Reader.minFrequencySmooth)
                    self.SummaryFigureCanvas.scatter(Reader.time, yPlot, 20, readerColor)
            self.SummaryFigureCanvas.saveAs(f'{self.savePath}/Summary Figure.jpg')
            self.SummaryFigureCanvas.drawCanvas(frame)
        except:
            logging.exception("Failed to generate summaryPlot")

    def createSummaryAnalyzedFile(self):
        rowHeaders = ['Time (hours)']
        rowData = [self.Readers[0].time]
        with open(f'{self.savePath}/summaryAnalyzed.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for Reader in self.Readers:
                rowHeaders.append(f'Reader {Reader.readerNumber} SGI')
                readerSGI = frequencyToIndex(Reader.zeroPoint, Reader.minFrequencySmooth)
                rowData.append(readerSGI)
            writer.writerow(rowHeaders)
            # array transpose converts it to write columns instead of rows
            writer.writerows(np.array(rowData).transpose())
        return

    def onClosing(self):
        if tk.messagebox.askokcancel("Exit", "Are you sure you want to close the program?"):
            self.root.destroy()

    def resetRun(self):
        for widgets in self.readerPlotFrame.winfo_children():
            widgets.destroy()
        if self.freqToggleSet == "SGI":
            self.createEndOfExperimentView()
        else:
            self.Buttons.createGuidedSetupButton(self.readerPlotFrame)
            self.Buttons.guidedSetupButton.invoke()
        for Reader in self.Readers:
            try:
                Reader.zeroPoint = 1
                Reader.ReaderInterface.close()
            except AttributeError:
                Reader.socket = None
                logging.exception(f'Failed to close Reader {Reader.readerNumber} socket')
        self.PortAllocator.resetPorts()
        self.freqToggleSet = "Signal Check"
        self.thread = threading.Thread(target=self.mainLoop, args=())
        self.foundPorts = False
        self.Buttons.ReaderInterfaces = []
        self.Readers = []

    def createEndOfExperimentView(self):
        endOfExperimentFrame = tk.Frame(self.root, bg=self.white)
        endOfExperimentFrame.place(relx=0, rely=0.05, relwidth=1, relheight=0.9)
        endOfExperimentFrame.grid_rowconfigure(0, weight=1)
        endOfExperimentFrame.grid_rowconfigure(1, weight=10)
        endOfExperimentFrame.grid_rowconfigure(2, weight=1)
        endOfExperimentFrame.grid_columnconfigure(0, weight=2)
        endOfExperimentFrame.grid_columnconfigure(1, weight=3)

        fileExplorerLabel = tk.Label(endOfExperimentFrame, text='Experiment File Location: ', bg='white')
        fileExplorerLabel.grid(row=0, column=0, sticky='ne', padx=10)
        fileExplorerButton = ttk.Button(endOfExperimentFrame, text=self.savePath,
                                       command=lambda: helper_functions.openFileExplorer(self.savePath))
        fileExplorerButton.grid(row=0, column=1, sticky='nw', padx=10)
        fileExplorerButton['style'] = 'W.TButton'

        self.guidedSetupImage = ImageTk.PhotoImage(file=f'{self.savePath}/setupForm.png')
        image_label = tk.Label(endOfExperimentFrame, image=self.guidedSetupImage, bg=self.white)
        image_label.grid(row=1, column=0, sticky='nesw')

        image = Image.open(f'{self.savePath}/Summary Figure.jpg').resize((600, 400), Image.ANTIALIAS)
        self.summaryPlotImage = ImageTk.PhotoImage(image)
        image_label = tk.Label(endOfExperimentFrame, image=self.summaryPlotImage, bg=self.white)
        image_label.grid(row=1, column=1, sticky='nesw')

        self.Buttons.createGuidedSetupButton(endOfExperimentFrame)
        self.Buttons.guidedSetupButton.grid(row=2, column=1, sticky='se', padx=10, pady=10)
        self.Buttons.guidedSetupButton['style'] = 'W.TButton'

        self.SummaryFigureCanvas.frequencyCanvas = None
        self.endOfExperimentFrame = endOfExperimentFrame


    def showFrame(self, frame):
        self.currentFrame = frame
        try:
            frame.place(relx=0, rely=0.05, relwidth=1, relheight=0.9)
            frame.tkraise()
        except:
            logging.exception('Failed to change the frame visible')
        self.summaryFrame.tkraise()


def incrementScan(Reader):
    Reader.scanNumber += Reader.scanRate


def deleteScanFile(filename):
    os.remove(filename)


def runShScript(shScriptFilename, desktop):
    st = os.stat(shScriptFilename)
    os.chmod(shScriptFilename, st.st_mode | stat.S_IEXEC)
    logFile = open(f'{desktop}/Calibration/log.txt', 'w+')
    process = subprocess.Popen(["sudo", "-SH", "sh", shScriptFilename], stdout=logFile, stderr=logFile, stdin=subprocess.PIPE, cwd=os.path.dirname(shScriptFilename))
    process.communicate("skroot".encode())
    process.wait()
