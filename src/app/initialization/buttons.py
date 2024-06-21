import logging
import os
import threading
import time
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from src.app.widget import text_notification
from src.app.exception.common_exceptions import UserExitedException
from src.app.widget.information_panel import InformationPanel
from src.app.sib.reader_interface import ReaderInterface
from src.app.sib.sib import Sib


class ButtonFunctions:
    def __init__(self, AppModule, location, root, PortAllocator):
        self.root = root
        image = Image.open(rf"{location}/../resources/help.png")
        resizedImage = image.resize((15, 15), Image.LANCZOS)
        self.helpIcon = ImageTk.PhotoImage(resizedImage)
        self.AppModule = AppModule
        self.ReaderInterfaces = []
        self.PortAllocator = PortAllocator
        self.createButtonsOnNewFrame()

    def createButtonsOnNewFrame(self):
        self.startButton = ttk.Button(self.AppModule.readerPlotFrame, text="Start Experiment", style='W.TButton',
                                      command=lambda: self.startFunc())
        self.AppModule.summaryFrame = tk.Frame(self.AppModule.readerPlotFrame, bg=self.AppModule.white, bd=0)
        self.AppModule.summaryPlotButton = ttk.Button(self.AppModule.readerPlotFrame, text="Summary Plot Update",
                                                      command=lambda: self.AppModule.plotSummary(self.AppModule.summaryFrame))
        self.stopButton = ttk.Button(self.AppModule.readerPlotFrame, text="End Experiment", style='W.TButton',
                                     command=lambda: self.stopFunc())
        self.helpButton = ttk.Button(self.root, text="Need help?", image=self.helpIcon, compound=tk.LEFT, style='W.TButton',
                                     command=lambda: InformationPanel(self.AppModule, self.helpIcon, self.root))

    def startFunc(self):
        spaceForPlots = 0.9
        self.AppModule.summaryFrame.place(rely=0.5 * spaceForPlots, relx=0.67, relwidth=0.3,
                                          relheight=0.45 * spaceForPlots)
        self.AppModule.threadStatus = self.AppModule.thread.is_alive()
        self.startButton.destroy()
        if not self.AppModule.ServerFileShare.disabled and self.AppModule.os == "windows":
            self.AppModule.ServerFileShare.makeNextFolder(os.path.basename(self.AppModule.savePath))
        self.AppModule.Settings.createReaders(self.AppModule.numReaders, self.ReaderInterfaces)
        self.AppModule.Settings.addReaderNotes()
        self.AppModule.Settings.addReaderSecondAxis()
        self.AppModule.Settings.addInoculation()
        self.placeStopButton()
        self.AppModule.Timer.createWidget(self.AppModule.readerPlotFrame)
        text_notification.setText("Scanning...")
        logging.info("started")
        if self.AppModule.threadStatus:
            tk.messagebox.showinfo("Error", "Test Still Running")
        else:
            self.AppModule.thread.start()

    def stopFunc(self):
        endExperiment = tk.messagebox.askquestion('End Experiment', 'Are you sure you wish to end the experiment?')
        if endExperiment == 'yes':
            logging.info('Experiment ended by user.')
            try:
                self.AppModule.thread.shutdown_flag.set()
            except:
                text_notification.setText("Experiment Ended.", ('Courier', 9, 'bold'), self.AppModule.royalBlue,
                                          self.AppModule.white)
                self.AppModule.resetRun()
            self.stopButton.destroy()
            text_notification.setText("Ending experiment once current sweep is complete.", ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)

    def findReaders(self, numReaders):
        logging.info(f'calibrate button pressed')
        for readerNumber in range(1, numReaders + 1):
            try:
                port = self.findPort(readerNumber)
                self.ReaderInterfaces.append(instantiateReader(port, self.AppModule, readerNumber, True))
            except UserExitedException:
                self.AppModule.root.destroy()
                logging.exception("User exited during port finding.")
                raise
            except:
                logging.exception(f'Failed to instantiate reader {readerNumber}')

    def calFunc(self, numReaders):
        calThreads = []
        for readerIndex in range(numReaders):
            self.calFunc2(readerIndex)
            # calThread = threading.Thread(target=self.calFunc2, args=(readerIndex,), daemon=True)
            # calThreads.append(calThread)
            # calThread.start()
        return calThreads

    def calibrateReaders(self):
        self.calibrateReadersButton.destroy()
        calibrateReadersThread = threading.Thread(target=self.calibrateReaders1, daemon=True)
        calibrateReadersThread.start()

    def calibrateReaders1(self):
        text_notification.setText("Calibrating readers... do not move them", ('Courier', 9, 'bold'),
                                  self.AppModule.royalBlue, self.AppModule.white)
        threads = self.calFunc(self.AppModule.numReaders)
        for t in threads:
            t.join()
        calibrationFailed = False
        readersCalibrationFailed = ""
        for ReaderInterface in self.ReaderInterfaces:
            if ReaderInterface.calibrationFailed:
                calibrationFailed = True
                text_notification.setText(f"Calibration failed for reader {ReaderInterface.readerNumber}",
                                          ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)
                readersCalibrationFailed = readersCalibrationFailed.join(f" {ReaderInterface.readerNumber}")
        if calibrationFailed:
            text_notification.setText(f"Calibration failed for readers:{readersCalibrationFailed}",
                                      ('Courier', 9, 'bold'),
                                      self.AppModule.royalBlue, self.AppModule.white)
            self.placeStopButton()
        else:
            text_notification.setText(f"Calibration Complete", ('Courier', 9, 'bold'),
                                      self.AppModule.royalBlue, self.AppModule.white)
            self.placeStartButton()

    def calFunc2(self, readerIndex):
        try:
            logging.info(f"Calibrating reader {readerIndex + 1}")
            self.ReaderInterfaces[readerIndex].calibrateIfRequired()
            logging.info(f"Calibration complete for reader {readerIndex + 1}")
            self.ReaderInterfaces[readerIndex].loadCalibrationFile()
        except:
            self.ReaderInterfaces[readerIndex].calibrationFailed = True
            logging.exception(f'Failed to calibrate reader {readerIndex + 1}')

    def connectReaders(self, numReaders):
        self.connectReadersButton.destroy()
        for readerNumber in range(1, numReaders + 1):
            try:
                port = self.findPort(readerNumber)
                self.ReaderInterfaces.append(instantiateReader(port, self.AppModule, readerNumber, False))
            except UserExitedException:
                self.AppModule.root.destroy()
                logging.exception("User exited during port finding.")
                raise
        self.AppModule.foundPorts = True
        self.placeStartButton()

    def findPort(self, readerNumber):
        if not self.AppModule.isDevMode:
            filteredPorts, attempts, port = [], 0, ''
            pauseUntilUserClicks(readerNumber)
            while filteredPorts == [] and attempts <= 3:
                time.sleep(2)
                try:
                    port = self.PortAllocator.getNewPort()
                    return port
                except:
                    attempts += 1
                    if attempts > 3:
                        tk.messagebox.showerror(f'Reader {readerNumber}',
                                               f'Reader {readerNumber}\nNew Reader not found more than 3 times,\nApp Restart required.')
                        break
                    else:
                        shouldContinue = tk.messagebox.askokcancel(f'Reader {readerNumber}',
                                               f'Reader {readerNumber}\nNew Reader not found, ensure a new Reader is plugged in, then press OK\n'
                                               f'Press cancel to shutdown the app.')
                        if not shouldContinue:
                            break
            raise UserExitedException("The user chose not to go forward during port finding.")
        else:
            return '', ''

    def placeStartButton(self):
        self.startButton.place(relx=0.46, rely=0.47)

    def placeStopButton(self):
        self.stopButton.pack(side='top', anchor='ne')

    def placeHelpButton(self):
        self.helpButton.pack(side='bottom', anchor='se')

    def placeConnectReadersButton(self):
        self.connectReadersButton = ttk.Button(self.AppModule.readerPlotFrame, text="Connect Readers", style='W.TButton',
                                               command=lambda: self.connectReaders(self.AppModule.numReaders))
        self.connectReadersButton.place(relx=0.46, rely=0.47)

    def placeCalibrateReadersButton(self):
        self.calibrateReadersButton = ttk.Button(self.AppModule.readerPlotFrame, text="Calibrate", style='W.TButton',
                                                 command=lambda: self.calibrateReaders())
        self.calibrateReadersButton.place(relx=0.46, rely=0.47)

    def createGuidedSetupButton(self, frame):
        self.guidedSetupButton = ttk.Button(frame, text="Start new experiment", style='W.TButton',
                                            command=lambda: self.AppModule.guidedSetup(self.AppModule.month,
                                                                                       self.AppModule.day,
                                                                                       self.AppModule.year,
                                                                                       self.AppModule.numReaders,
                                                                                       self.AppModule.scanRate,
                                                                                       self.AppModule.cellType,
                                                                                       self.AppModule.secondAxisTitle,
                                                                                       self.AppModule.equilibrationTime))



    def placeGuidedSetupButton(self, frame):
        self.createGuidedSetupButton(frame)
        self.guidedSetupButton.pack(side='bottom', anchor='ne')


def pauseUntilUserClicks(readerNumber):
    tk.messagebox.showinfo(f'Reader {readerNumber}',
                           f'Reader {readerNumber}\nPress OK when reader {readerNumber} is plugged in')


def instantiateReader(port, AppModule, readerNumber, calibrationRequired) -> ReaderInterface:
    try:
        sib = Sib(port, f'{AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv', readerNumber, AppModule.PortAllocator, calibrationRequired)
        success = sib.performHandshake()
        if success:
            return sib
        else:
            logging.info(f"Failed to handshake SIB #{readerNumber} on port {port}")
            text_notification.setText("Failed to connect to SiB")
            sib.close()
    except:
        logging.exception(f"Failed to instantiate reader {readerNumber}")

