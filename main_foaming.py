import importlib.util
import math
import os
import sys
import threading
import time
import tkinter as tk

import matplotlib as mpl
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure

import logger
import setup
import text_notification
from aws import AwsBoto3
from buttons import ButtonFunctions
from colors import ColorCycler
from dev import DevMode
from pdf import generatePdf
from server import ServerFileShare
from settings import Settings

mpl.use('TkAgg')


class AppModule:
    def __init__(self, version):
        self.currentFrame = None
        self.totalMin = None
        self.time = None
        self.frequency = None
        self.freq = None
        self.calFreq = None
        self.caldB = None
        self.calculatedCells = None
        self.dB = None
        self.notes = None
        self.viabilityTime = None
        self.totalViability = None
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
        self.browseButton = None
        self.menubar = None
        try:
            self.desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            self.os = 'windows'
        except:
            self.desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
            self.os = 'linux'
        logger.loggerSetup(f'{self.desktop}/Calibration/log.txt', version)
        self.numReaders = None
        self.savePath = ''
        self.cellApp = False
        self.foamingApp = True
        self.freqToggleSet = "Signal Check"
        self.splineToggleSet = False
        self.denoiseSet = True
        self.currentlyScanning = False
        self.disableSaveFullFiles = False
        self.emailSetting = False
        self.awsTimeBetweenUploads = 6
        self.awsLastUploadTime = 0
        self.scanRate = 0.5
        self.startFreq = 40
        self.stopFreq = 250
        self.nPoints = 2000
        self.airFreq = 0
        self.waterFreq = 0
        self.waterShift = None
        self.thread = ''
        self.threadStatus = ''
        self.royalBlue = 'RoyalBlue4'
        self.white = 'white'
        self.ports = []
        try:
            self.location = sys._MEIPASS
        except:
            self.location = os.getcwd()
        self.root()
        self.ColorCycler = ColorCycler()
        self.ServerFileShare = ServerFileShare(self)
        self.Readers = []
        self.Settings = Settings(self)
        self.Buttons = ButtonFunctions(self)
        self.DevMode = DevMode()
        if not self.DevMode.isDevMode:
            self.aws = AwsBoto3()
        self.isDevMode = self.DevMode.isDevMode
        self.setupApp()
        self.Buttons.startFunc()

    def setupApp(self):
        self.Setup = setup.Setup(self.root, self.Buttons, self.Settings, self)
        self.menubar = self.Setup.createMenus()
        self.Setup.createTheme()
        self.Setup.createFrames()
        self.root.config(menu=self.menubar)
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            import pyi_splash
            pyi_splash.close()
        self.root.mainloop()  # everything comes before this

    def root(self):
        self.root = tk.Tk()  # everything in the application comes after this
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
            try:
                startTime = time.time()
                for Reader in self.Readers:
                    if not self.isDevMode:
                        success = Reader.takeScan()
                        if not success:
                            text_notification.setText(f"Reader {Reader.readerNumber} \nFailed to take scan.")
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
                        Reader.deleteScanFile()
                    Reader.printScanFreq()
                    Reader.checkFoaming()
                    Reader.checkContamination()
                    Reader.checkHarvest()
                    Reader.incrementScan()
                self.summaryPlotButton.invoke()  # any changes to GUI must be in main thread
                generatePdf(self.savePath, self.Readers)
                self.awsUploadFile()
                currentTime = time.time()
                self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
            except:
                logger.exception('Unknown error has occurred')
        text_notification.setText("Stopped.", ('Courier', 9, 'bold'), self.royalBlue, self.white)
        self.resetRun()
        logger.info('Stopped scanning')

    def awsUploadFile(self):
        if not self.DevMode.isDevMode:
            if (self.Readers[0].scanNumber - self.awsLastUploadTime) > self.awsTimeBetweenUploads:
                self.aws.uploadFile(f'{self.savePath}/Summary.pdf')
                self.awsLastUploadTime = self.Readers[0].scanNumber

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
            if self.thread.shutdown_flag.is_set() == True:
                logger.info('Cancelling data collection due to stop button pressed')
                break
            time.sleep(0.5)
            currentTime = time.time()

    def plotSummary(self):
        try:
            try:
                self.summaryFig.clear()
            except:
                size = 3
                self.summaryFig = Figure(figsize=(size, size))
                self.summaryFig.set_tight_layout(True)
            self.summaryPlot = self.summaryFig.add_subplot(111)
            self.summaryPlot.tick_params(axis='both', which='minor', labelsize=7)
            self.summaryPlot.tick_params(axis='both', which='major', labelsize=7)
            self.ColorCycler.reset()
            if self.freqToggleSet == "Frequency" or self.freqToggleSet == "Signal Check":
                self.summaryPlot.set_ylabel('Change in Frequency (MHz)', fontsize=9)
                self.summaryPlot.set_title(f'Resonant Frequency Summary', fontsize=9)
                for Reader in self.Readers:
                    readerColor = self.ColorCycler.getNext()
                    if self.denoiseSet:
                        y = [yval - Reader.denoiseFrequencySmooth[0] for yval in Reader.denoiseFrequencySmooth]
                        self.summaryPlot.scatter(Reader.denoiseTimeSmooth, y, s=20, color=readerColor)
                    else:
                        y = [yval - Reader.minFrequencySmooth[0] for yval in Reader.minFrequencySmooth]
                        self.summaryPlot.scatter(Reader.time, y, s=20, color=readerColor)
            elif self.freqToggleSet == "Signal Strength":
                self.summaryPlot.set_ylabel('Change in Signal Strength (dB)', fontsize=9)
                self.summaryPlot.set_title(f'Signal Strength Summary', fontsize=9)
                for Reader in self.Readers:
                    readerColor = self.ColorCycler.getNext()
                    if self.denoiseSet:
                        y = [yval - Reader.denoiseTotalMinSmooth[0] for yval in Reader.denoiseTotalMinSmooth]
                        self.summaryPlot.scatter(Reader.denoiseTimedBSmooth, y, s=20, color=readerColor)
                    else:
                        y = [yval - Reader.minDb[0] for yval in Reader.minDbSmooth]
                        self.summaryPlot.scatter(Reader.time, y, s=20, color=readerColor)
            self.summaryPlot.set_xlabel('Time (hours)', fontsize=7)
            self.summaryFig.savefig(f'{self.savePath}/Summary Figure.jpg')
            try:
                self.summaryCanvas.get_tk_widget().pack()
            except:
                self.summaryCanvas = FigureCanvasTkAgg(self.summaryFig, master=self.summaryFrame)
            self.summaryCanvas.draw()
            self.summaryCanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except:
            logger.exception("Failed to generated summaryPlot")

    def resetRun(self):
        self.airFreqInput.delete(0, 50)
        self.waterFreqInput.delete(0, 50)
        self.totalViability = []
        self.viabilityTime = []
        self.waterShift = None
        self.notes = ['']
        self.calculatedCells = []
        self.ports = []
        self.caldB = []
        self.calFreq = []
        self.freq = [None]
        self.dB = [None]
        self.frequency = [[]]
        self.time = [[]]
        self.totalMin = [[]]
        self.dB = [None]
        self.freq = [None]
        self.frequency = [[]]
        self.time = [[]]
        self.totalMin = [[]]
        self.savePath = ''  # needs edited # needs to call reset readers specifically
        try:
            self.menubar.delete("Inoculation")
        except:
            pass
        try:
            self.menubar.delete("Experiment Notes")
        except:
            pass
        try:
            self.menubar.delete("Second Axis")
        except:
            pass
        for Reader in self.Readers:
            try:
                Reader.socket.close()
            except:
                Reader.socket = None
                logger.exception(f'Failed to close Reader {Reader.readerNumber} socket')
            try:
                Reader.indicatorCanvas.delete('all')
            except:
                logger.exception(f'Failed to remove indicator for Reader {Reader.readerNumber}')
            try:
                for widget in Reader.frequencyFrame.winfo_children():
                    widget.destroy()
            except:
                logger.exception(f'Failed to remove canvas for Reader {Reader.readerNumber}')
        for widgets in self.summaryFrame.winfo_children():
            widgets.destroy()
        self.Readers = []

    def showFrame(self, frame):
        self.currentFrame = frame
        try:
            frame.place(relx=0, rely=0.05, relwidth=1, relheight=0.9)
            frame.tkraise()
        except:
            logger.exception('Failed to change the frame visible')


AppModule("version: Unified_v3.1")
