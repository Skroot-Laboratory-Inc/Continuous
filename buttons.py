import os
import subprocess as sp
import threading
import time
import tkinter as tk
from tkinter import ttk

from serial.tools import list_ports
from PIL import Image, ImageTk

import logger
import text_notification
from sib import Sib
from vna import VnaScanning
from information_panel import InformationPanel


class ButtonFunctions:
    def __init__(self, AppModule, location, root):
        self.root = root
        image = Image.open(rf"{location}/resources/help.png")
        resizedImage = image.resize((15, 15), Image.LANCZOS)
        self.helpIcon = ImageTk.PhotoImage(resizedImage)
        self.AppModule = AppModule
        self.ReaderInterfaces = []

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
        self.AppModule.threadStatus = self.AppModule.thread.is_alive()
        self.startButton.destroy()
        if not self.AppModule.ServerFileShare.disabled and self.AppModule.os == "windows":
            self.AppModule.ServerFileShare.makeNextFolder(os.path.basename(self.AppModule.savePath))
        self.AppModule.Settings.createReaders(self.AppModule.numReaders, self.ReaderInterfaces)
        self.AppModule.Settings.addReaderNotes()
        self.AppModule.Settings.addReaderSecondAxis()
        if self.AppModule.cellApp:
            self.AppModule.Settings.addInoculation()
        self.createStopButton(self.AppModule.readerPlotFrame)
        self.AppModule.Timer.createWidget(self.AppModule.readerPlotFrame)
        text_notification.setText("Scanning...")
        logger.info("started")
        if self.AppModule.threadStatus:
            tk.messagebox.showinfo("Error", "Test Still Running")
        else:
            self.AppModule.thread.start()

    def createStopButton(self, frame):
        self.stopButton = ttk.Button(frame, text="Stop", command=lambda: self.stopFunc())
        self.stopButton.pack(side='top', anchor='ne')
        self.stopButton['style'] = 'W.TButton'

    def createHelpButton(self, frame):
        self.helpButton = ttk.Button(frame, text="Need help?", image=self.helpIcon, compound=tk.LEFT,
                                     command=lambda: InformationPanel(self.AppModule, self.helpIcon, self.root))
        self.helpButton.pack(side='bottom', anchor='ne')
        self.helpButton['style'] = 'W.TButton'

    def stopFunc(self):
        logger.info("Stop Button Pressed")
        self.AppModule.thread.shutdown_flag.set()
        self.stopButton.destroy()
        text_notification.setText("Stopping...", ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)

    def calFunc(self, numReaders, AppModule):
        logger.info(f'calibrate button pressed')
        calThread = threading.Thread(target=self.calFunc2, args=(numReaders, AppModule))
        calThread.start()

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
                try:
                    sib = Sib(calFileLocation, port, self.AppModule, readerNumber, True)
                    success = sib.performHandshake()
                    if success:
                        self.ReaderInterfaces.append(sib)
                    else:
                        sib.close()
                        Vna = VnaScanning(calFileLocation, port, self.AppModule, readerNumber, True)
                        self.ReaderInterfaces.append(Vna)
                except:
                    logger.exception("SIB Handshake failed - can ignore if VNA is connected")
                    Vna = VnaScanning(calFileLocation, port, self.AppModule, readerNumber, True)
                    self.ReaderInterfaces.append(Vna)
                text_notification.setText(f"Calibration {readerNumber} Complete", ('Courier', 9, 'bold'),
                                          self.AppModule.royalBlue, self.AppModule.white)
                logger.info(f"Calibration complete for reader {readerNumber}")
            except:
                logger.exception(f'Failed to calibrate reader {readerNumber}')

    def createConnectReadersButton(self):
        self.connectReadersButton = ttk.Button(self.AppModule.readerPlotFrame, text="Connect Readers",
                                               command=lambda: self.connectReaders(self.AppModule.numReaders))
        self.connectReadersButton.place(relx=0.46, rely=0.47)
        self.connectReadersButton['style'] = 'W.TButton'

    def connectReaders(self, numReaders):
        self.connectReadersButton.destroy()
        for readerNumber in range(1, numReaders + 1):
            port, readerType = self.findPort(readerNumber)
            calFileLocation = f'{self.AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv'
            try:
                if readerType == 'SIB':
                    sib = Sib(calFileLocation, port, self.AppModule, readerNumber, True)
                    success = sib.performHandshake()
                    if success:
                        self.ReaderInterfaces.append(sib)
                    else:
                        sib.close()
                elif readerType == 'VNA':
                        Vna = VnaScanning(calFileLocation, port, self.AppModule, readerNumber, True)
                        self.ReaderInterfaces.append(Vna)
            except:
                logger.exception("SIB Handshake failed - can ignore if VNA is connected")
                Vna = VnaScanning(calFileLocation, port, self.AppModule, readerNumber, True)
                self.ReaderInterfaces.append(Vna)
        self.AppModule.foundPorts = True
        self.createStartButton()

    def findPort(self, readerNumber):
        if not self.AppModule.isDevMode:
            filteredSIBPorts, filteredVNAPorts, attempts, port, readerType = [], [], 0, '', ''
            pauseUntilUserClicks(readerNumber)
            while filteredVNAPorts == [] and filteredSIBPorts == [] and attempts <= 3:
                time.sleep(2)
                ports = list_ports.comports()
                if self.AppModule.os == "windows":
                    filteredVNAPorts = [port.device for port in ports if "USB-SERIAL CH340" in port.description and port.device not in self.AppModule.ports]
                    filteredSIBPorts = [port.device for port in ports if "USB Serial Device" in port.description and port.device not in self.AppModule.ports]
                else:
                    filteredVNAPorts = [port.device for port in ports
                                        if port.description == "USB Serial" and port.device not in self.AppModule.ports]
                    filteredSIBPorts = [port.device for port in ports if
                                        port.manufacturer == "Skroot Laboratory" and port.device not in self.AppModule.ports]
                if filteredSIBPorts:
                    port = filteredSIBPorts[0]
                    readerType = 'SIB'
                if filteredVNAPorts:
                    port = filteredVNAPorts[0]
                    readerType = 'VNA'
                self.AppModule.ports.append(port)
                attempts += 1
                if attempts > 3:
                    tk.messagebox.showinfo(f'Reader {readerNumber}',
                                           f'Reader {readerNumber}\nNew VNA not found more than 3 times,\nApp restart required to avoid infinite loop')
            logger.info(f'{self.AppModule.ports}')
            return port, readerType

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
