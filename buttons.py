import os
import threading
import time
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

import logger
import text_notification
from information_panel import InformationPanel
from reader_interface import ReaderInterface
from sib import Sib
from vna import VnaScanning


class ButtonFunctions:
    def __init__(self, AppModule, location, root):
        self.root = root
        image = Image.open(rf"{location}/resources/help.png")
        resizedImage = image.resize((15, 15), Image.LANCZOS)
        self.helpIcon = ImageTk.PhotoImage(resizedImage)
        self.AppModule = AppModule
        self.ReaderInterfaces = []
        self.createButtonsOnNewFrame()

    def createButtonsOnNewFrame(self):
        self.startButton = ttk.Button(self.AppModule.readerPlotFrame, text="Start", command=lambda: self.startFunc())
        self.AppModule.summaryFrame = tk.Frame(self.AppModule.readerPlotFrame, bg=self.AppModule.white, bd=0)
        self.AppModule.summaryPlotButton = ttk.Button(self.AppModule.readerPlotFrame, text="Summary Plot Update",
                                                      command=lambda: self.AppModule.plotSummary())
        self.stopButton = ttk.Button(self.AppModule.readerPlotFrame, text="Stop", command=lambda: self.stopFunc())
        self.helpButton = ttk.Button(self.AppModule.readerPlotFrame, text="Need help?", image=self.helpIcon,
                                     compound=tk.LEFT,
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
        if self.AppModule.cellApp:
            self.AppModule.Settings.addInoculation()
        self.placeStopButton()
        self.AppModule.Timer.createWidget(self.AppModule.readerPlotFrame)
        text_notification.setText("Scanning...")
        logger.info("started")
        if self.AppModule.threadStatus:
            tk.messagebox.showinfo("Error", "Test Still Running")
        else:
            self.AppModule.thread.start()

    def stopFunc(self):
        logger.info("Stop Button Pressed")
        self.AppModule.thread.shutdown_flag.set()
        self.stopButton.destroy()
        text_notification.setText("Stopping...", ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)

    def calFunc(self, numReaders):
        logger.info(f'calibrate button pressed')
        calThread = threading.Thread(target=self.calFunc2, args=numReaders)
        calThread.start()

    def calFunc2(self, numReaders):
        for readerNumber in range(1, numReaders + 1):
            text_notification.setText(f"Calibrating reader {readerNumber}... do not touch the reader",
                                      ('Courier', 9, 'bold'), self.AppModule.royalBlue,
                                      self.AppModule.white)
            try:
                logger.info(f"Calibrating reader {readerNumber}")
                port, readerType = self.findPort(readerNumber)
                self.ReaderInterfaces.append(instantiateReader(readerType, port, self.AppModule, readerNumber, True))
                text_notification.setText(f"Calibration {readerNumber} Complete", ('Courier', 9, 'bold'),
                                          self.AppModule.royalBlue, self.AppModule.white)
                logger.info(f"Calibration complete for reader {readerNumber}")
            except:
                logger.exception(f'Failed to calibrate reader {readerNumber}')

    def connectReaders(self, numReaders):
        self.connectReadersButton.destroy()
        for readerNumber in range(1, numReaders + 1):
            port, readerType = self.findPort(readerNumber)
            self.ReaderInterfaces.append(instantiateReader(readerType, port, self.AppModule, readerNumber, False))
        self.AppModule.foundPorts = True
        self.placeStartButton()

    def findPort(self, readerNumber):
        if not self.AppModule.isDevMode:
            filteredSIBPorts, filteredVNAPorts, attempts, port, readerType = [], [], 0, '', ''
            pauseUntilUserClicks(readerNumber)
            while filteredVNAPorts == [] and filteredSIBPorts == [] and attempts <= 3:
                time.sleep(2)
                try:
                    port, readerType = getNewVnaAndSibPorts(self.AppModule.os, self.AppModule.ports)
                    self.AppModule.ports.append(port)
                    return port, readerType
                except:
                    attempts += 1
                    if attempts > 3:
                        tk.messagebox.showinfo(f'Reader {readerNumber}',
                                               f'Reader {readerNumber}\nNew Reader not found more than 3 times,\nApp restart required to avoid infinite loop')
                    else:
                        tk.messagebox.showinfo(f'Reader {readerNumber}',
                                               f'Reader {readerNumber}\nNew Reader not found, ensure a new Reader is plugged in, then press OK')
        else:
            return '', ''

    def placeStartButton(self):
        self.startButton.place(relx=0.47, rely=0.47)
        self.startButton['style'] = 'W.TButton'

    def placeStopButton(self):
        self.stopButton.pack(side='top', anchor='ne')
        self.stopButton['style'] = 'W.TButton'

    def placeHelpButton(self):
        self.helpButton.pack(side='bottom', anchor='ne')
        self.helpButton['style'] = 'W.TButton'

    def placeConnectReadersButton(self):
        self.connectReadersButton = ttk.Button(self.AppModule.readerPlotFrame, text="Connect Readers",
                                               command=lambda: self.connectReaders(self.AppModule.numReaders))
        self.connectReadersButton.place(relx=0.46, rely=0.47)
        self.connectReadersButton['style'] = 'W.TButton'

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


def instantiateReader(readerType, port, AppModule, readerNumber, calibrationRequired) -> ReaderInterface:
    try:
        if readerType == 'SIB':
            sib = Sib(port, AppModule, readerNumber, calibrationRequired)
            success = sib.performHandshake()
            if success:
                return sib
            else:
                logger.info(f"Failed to handshake SIB {readerNumber}")
                text_notification.setText("Failed to connect to SiB")
                sib.close()
        elif readerType == 'VNA':
            return VnaScanning(port, AppModule, readerNumber, calibrationRequired)
    except:
        logger.exception(f"Failed to instantiate reader {readerNumber}")


def getNewVnaAndSibPorts(currentOs, portsTaken) -> (ListPortInfo, str):
    ports = list_ports.comports()
    if currentOs == "windows":
        filteredVNAPorts = [port.device for port in ports if
                            "USB-SERIAL CH340" in port.description and port.device not in portsTaken]
        filteredSIBPorts = [port.device for port in ports if
                            "USB Serial Device" in port.description and port.device not in portsTaken]
    else:
        filteredVNAPorts = [port.device for port in ports
                            if port.description == "USB Serial" and port.device not in portsTaken]
        filteredSIBPorts = [port.device for port in ports if
                            port.manufacturer == "Skroot Laboratory" and port.device not in portsTaken]
    if filteredSIBPorts:
        return filteredSIBPorts[0], 'SIB'
    if filteredVNAPorts:
        return filteredVNAPorts[0], 'VNA'
    raise Exception("No ports found")
