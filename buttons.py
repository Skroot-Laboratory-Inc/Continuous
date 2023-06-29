import os
import threading
import tkinter as tk
from tkinter.filedialog import askdirectory

import logger
import text_notification


class ButtonFunctions:
    def __init__(self, AppModule):
        self.AppModule = AppModule

    def browseFunc(self):
        savePath = askdirectory()
        if savePath != '':
            self.AppModule.savePath = savePath
            logger.info(f'savePath changed to {savePath}')
            self.AppModule.startButton['state'] = 'normal'
            if self.AppModule.numReaders == None:
                self.AppModule.numReaders = 1
            self.AppModule.ServerFileShare.makeNextFolder(os.path.basename(savePath))
            self.AppModule.Settings.createReaders(self.AppModule.numReaders)
            self.AppModule.Settings.addReaderNotes()
            self.AppModule.Settings.addReaderSecondAxis()
            if self.AppModule.cellApp:
                self.AppModule.Settings.addInoculation()
            text_notification.setText("Press start to begin\nthe experiment", ('Courier', 9, 'bold'),
                                      self.AppModule.royalBlue, self.AppModule.white)

    def startFunc(self):
        self.AppModule.summaryPlotButton['state'] = 'normal'
        self.AppModule.stopButton['state'] = 'normal'
        self.AppModule.submitButton['state'] = 'normal'
        logger.info(f'start button pressed')
        try:
            self.AppModule.threadStatus = self.AppModule.thread.is_alive()
        except:
            self.AppModule.threadStatus = False
        try:
            if self.AppModule.threadStatus == True:
                tk.messagebox.showinfo("Error", "Test Still Running")
            else:
                self.AppModule.thread = threading.Thread(target=self.AppModule.mainLoop, args=())
                self.AppModule.thread.start()
                self.AppModule.startButton['state'] = 'disabled'
                text_notification.setText("Press stop to end\nthe experiment", ('Courier', 9, 'bold'),
                                          self.AppModule.royalBlue, self.AppModule.white)
        except:
            raise
            tk.messagebox.showinfo("Error", "Please calibrate your reader first")
            logger.exception("Failed to calibrate the reader")

    def stopFunc(self):
        logger.info("Stop Button Pressed")
        self.AppModule.thread.shutdown_flag.set()
        text_notification.setText("Stopping...", ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)

    def helpFunc(self):
        tk.messagebox.showinfo("Help Box",
                               "Watch the status bar, below the logo for updates\n \nButton Descriptions: \n \nSubmit: Submit frequencies entered from previous experiment \nBrowse: Select a save location \nStart: Begin taking data, \nStop: Stop taking data \nSettings (menubar): used to change scan settings \nCalibrate: Re-calibrates the reader, ENSURE no sensor attached.")

    def calFunc(self):
        try:
            logger.info(f'calibrate button pressed')
            calThread = threading.Thread(target=self.calFunc2, args=())
            calThread.start()
        except:
            tk.messagebox.showinfo("Error", "Please select a save location first")
            logger.exception("Failed to select a save directory")

    def calFunc2(self):
        text_notification.setText("Calibrating...", ('Courier', 9, 'bold'), self.AppModule.royalBlue,
                                  self.AppModule.white)
        for Reader in self.AppModule.Readers:
            try:
                logger.info('calibrating')
                print('calibrating')
                if not os.path.exists(os.path.dirname(Reader.calFileLocation)):
                    os.mkdir(os.path.dirname(Reader.calFileLocation))
                Reader.readVna(0.1, 250, 10000, f'{Reader.calFileLocation}', Reader.port)
                text_notification.setText(f"Calibration {Reader.readerNumber} Complete", ('Courier', 9, 'bold'),
                                          self.AppModule.royalBlue, self.AppModule.white)
            except:
                text_notification.setText(f"Calibration Failed \nfor reader {Reader.readerNumber}...",
                                          ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)
                logger.exception(f'Failed to calibrate reader {Reader.readerNumber}')

    def submitFunc(self):
        try:
            logger.info('submit button pressed')
            if self.AppModule.airFreqInput.get() != '':
                self.AppModule.airFreq = float(self.AppModule.airFreqInput.get())
                self.AppModule.airFreqInput['state'] = 'disabled'
                logger.info(f'air: {self.AppModule.airFreq}')
            if self.AppModule.waterFreqInput.get() != '':
                self.AppModule.waterFreq = float(self.AppModule.waterFreqInput.get())
                self.AppModule.waterFreqInput['state'] = 'disabled'
                logger.info(f'water: {self.AppModule.waterFreq}')
        except:
            logger.exception('Air/Liquid input failure')
            tk.messagebox.showinfo("Error", "Empty air or liquid frequencies")
        try:
            self.AppModule.waterShift = self.AppModule.airFreq - self.AppModule.waterFreq
            for Reader in self.AppModule.Readers:
                Reader.initializeFoaming(self.AppModule.airFreq, self.AppModule.waterFreq, self.AppModule.waterShift)
            text_notification.setText(f"Foaming entry submitted. \n Shift: {round(self.AppModule.waterShift, 3)} MHz",
                                      ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)
        except:
            logger.exception('Failed to find water shift')
