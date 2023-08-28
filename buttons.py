import os
import subprocess as sp
import threading
import time
import tkinter as tk
from tkinter import ttk

from serial.tools import list_ports

import logger
import text_notification
from vna import VnaScanning


class ButtonFunctions:
    def __init__(self, AppModule):
        self.AppModule = AppModule
        self.Vnas = []

    def createStartButton(self):
        self.startButton = ttk.Button(self.AppModule.readerPlotFrame, text="Start", command=lambda: self.startFunc())
        self.startButton.place(relx=0.47, rely=0.47)
        self.startButton['style'] = 'W.TButton'

    def startFunc(self):
        spaceForPlots = 0.9
        self.AppModule.summaryFrame = tk.Frame(self.AppModule.readerPlotFrame, bg=self.AppModule.white, bd=0)
        self.AppModule.summaryFrame.place(rely=0.5 * spaceForPlots, relx=0.67, relwidth=0.3,
                                          relheight=0.45 * spaceForPlots)

        # Other buttons that will be invoked
        self.AppModule.summaryPlotButton = ttk.Button(self.AppModule.readerPlotFrame, text="Summary Plot Update",
                                                      command=lambda: self.AppModule.plotSummary())
        try:
            self.AppModule.threadStatus = self.AppModule.thread.is_alive()
        except:
            self.AppModule.threadStatus = False
        self.startButton.destroy()
        if not self.AppModule.ServerFileShare.disabled:
            self.AppModule.ServerFileShare.makeNextFolder(os.path.basename(self.AppModule.savePath))
        self.AppModule.Settings.createReaders(self.AppModule.numReaders, self.Vnas)
        self.AppModule.Settings.addReaderNotes()
        self.AppModule.Settings.addReaderSecondAxis()
        if self.AppModule.cellApp:
            self.AppModule.Settings.addInoculation()
        self.createStopButton(self.AppModule.readerPlotFrame)
        self.AppModule.Timer.createWidget(self.AppModule.readerPlotFrame)
        try:
            text_notification.setText("Scanning...")
            logger.info("started")
            if self.AppModule.threadStatus:
                tk.messagebox.showinfo("Error", "Test Still Running")
            else:
                self.AppModule.thread.start()
        except:
            tk.messagebox.showinfo("Error", "Please calibrate your reader first")
            logger.exception("Failed to calibrate the reader")

    def createStopButton(self, frame):
        self.stopButton = ttk.Button(frame, text="Stop", command=lambda: self.stopFunc())
        self.stopButton.pack(side='top', anchor='ne')
        self.stopButton['style'] = 'W.TButton'

    def stopFunc(self):
        logger.info("Stop Button Pressed")
        self.AppModule.thread.shutdown_flag.set()
        self.stopButton.destroy()
        text_notification.setText("Stopping...", ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)

    def calFunc(self, numReaders, AppModule):
        try:
            logger.info(f'calibrate button pressed')
            calThread = threading.Thread(target=self.calFunc2, args=(numReaders, AppModule))
            calThread.start()
        except:
            tk.messagebox.showinfo("Error", "Please select a save location first")
            logger.exception("Failed to select a save directory")

    def calFunc2(self, numReaders, AppModule):
        for readerNumber in range(1, numReaders + 1):
            text_notification.setText(f"Calibrating reader {readerNumber}... do not touch the reader",
                                      ('Courier', 9, 'bold'), self.AppModule.royalBlue,
                                      self.AppModule.white)
            try:
                logger.info(f"Calibrating reader {readerNumber}")
                calFileLocation = f'{AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv'
                port = self.findPort(readerNumber)
                if not os.path.exists(os.path.dirname(calFileLocation)):
                    os.mkdir(os.path.dirname(calFileLocation))
                Vna = VnaScanning(calFileLocation, port, self.AppModule, True)
                self.Vnas.append(Vna)
                text_notification.setText(f"Calibration {readerNumber} Complete", ('Courier', 9, 'bold'),
                                          self.AppModule.royalBlue, self.AppModule.white)
                logger.info(f"Calibration complete for reader {readerNumber}")
            except:
                text_notification.setText(f"Calibration Failed \nfor reader {readerNumber}...",
                                          ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)
                logger.exception(f'Failed to calibrate reader {readerNumber}')

    def createConnectReadersButton(self):
        self.connectReadersButton = ttk.Button(self.AppModule.readerPlotFrame, text="Connect Readers",
                                               command=lambda: self.connectReaders(self.AppModule.numReaders))
        self.connectReadersButton.place(relx=0.46, rely=0.47)
        self.connectReadersButton['style'] = 'W.TButton'

    def connectReaders(self, numReaders):
        self.connectReadersButton.destroy()
        for readerNumber in range(1, numReaders + 1):
            port = self.findPort(readerNumber)
            calFileLocation = f'{self.AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv'
            Vna = VnaScanning(calFileLocation, port, self.AppModule, False)
            self.Vnas.append(Vna)
        self.AppModule.foundPorts = True
        self.createStartButton()

    def findPort(self, readerNumber):
        if self.AppModule.isDevMode == False:
            portList, attempts, port = [], 0, ''
            pauseUntilUserClicks(readerNumber)
            while portList == [] and attempts <= 3:
                time.sleep(2)
                if self.AppModule.os == "windows":
                    ports = list_ports.comports()
                    portNums = [int(ports[i][0][3:]) for i in range(len(ports))]
                    portList = [num for num in portNums if num not in self.AppModule.ports]
                    if portList != []:
                        port = f'COM{max(portList)}'
                        self.AppModule.ports.append(max(portList))
                else:
                    ports = sp.run('ls /dev/ttyUSB*', shell=True, capture_output=True).stdout.decode(
                        'ascii').strip().splitlines()
                    portList = [port for port in ports if port not in self.AppModule.ports]
                    if portList != []:
                        port = portList[-1]
                        self.AppModule.ports.append(max(portList))
                logger.info(f'Used: {self.AppModule.ports}, found: {portList}')
                attempts += 1
                if attempts > 3:
                    tk.messagebox.showinfo(f'Reader {readerNumber}',
                                           f'Reader {readerNumber}\nNew VNA not found more than 3 times,\nApp restart required to avoid infinite loop')
            logger.info(f'{self.AppModule.ports}')
            return port

    def createGuidedSetupButton(self):
        self.guidedSetupButton = ttk.Button(self.AppModule.root, text="",
                                            command=lambda: self.AppModule.guidedSetup(self.AppModule.month,
                                                                                       self.AppModule.day,
                                                                                       self.AppModule.year,
                                                                                       self.AppModule.numReaders,
                                                                                       self.AppModule.scanRate,
                                                                                       self.AppModule.cellType,
                                                                                       self.AppModule.vesselType,
                                                                                       self.AppModule.secondAxisTitle))


def pauseUntilUserClicks(readerNumber):
    tk.messagebox.showinfo(f'Reader {readerNumber}',
                           f'Reader {readerNumber}\nPress OK when reader {readerNumber} is plugged in')
