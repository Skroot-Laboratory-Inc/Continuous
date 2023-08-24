import importlib.util
import math
import os
import threading
import time
import tkinter as tk

import matplotlib as mpl
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure

import logger
import setup
import text_notification
from pdf import generatePdf

mpl.use('TkAgg')


class MainShared:
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

    def createRoot(self):
        self.root = tk.Tk()  # everything in the application comes after this
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
                            self.scanFrequency, self.scanMagnitude, self.scanPhase, success = Reader.Vna.takeScan(
                                f'{Reader.savePath}/{Reader.scanNumber}.csv', Reader.startFreq, Reader.stopFreq, Reader.nPoints)
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
                            deleteScanFile(f'{Reader.savePath}/{Reader.scanNumber}.csv')
                        Reader.printScanFreq()
                        Reader.checkFoaming()
                        Reader.checkContamination()
                        Reader.checkHarvest()
                    except:
                        logger.exception(f'reader {Reader.readerNumber} failed to take scan')
                    finally:
                        self.Timer.updateTime()
                        incrementScan(Reader)
                self.summaryPlotButton.invoke()  # any changes to GUI must be in main thread
                generatePdf(self.savePath, self.Readers)
                self.awsUploadFile()
            except:
                logger.exception('Unknown error has occurred')
            finally:
                currentTime = time.time()
                self.checkIfScanTookTooLong(currentTime - startTime)
                self.waitUntilNextScan(currentTime, startTime)
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
            time.sleep(0.05)
            self.Timer.updateTime()
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

    def onClosing(self):
        if tk.messagebox.askokcancel("Exit", "Are you sure you want to close the program?"):
            self.root.destroy()

    def resetRun(self):
        for Reader in self.Readers:
            try:
                Reader.Vna.closeSocket()
            except:
                Reader.socket = None
                logger.exception(f'Failed to close Reader {Reader.readerNumber} socket')
        for widgets in self.readerPlotFrame.winfo_children():
            widgets.destroy()
        self.Buttons.createConnectReadersButton()
        self.foundPorts = False
        self.ports = []
        self.Buttons.Vnas = []
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
