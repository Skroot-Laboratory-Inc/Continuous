import os
import threading
import tkinter as tk

import logger
import text_notification


class ButtonFunctions:
    def __init__(self, AppModule):
        self.AppModule = AppModule

    def browseFunc(self):
        if not self.AppModule.ServerFileShare.disabled:
            self.AppModule.ServerFileShare.makeNextFolder(os.path.basename(self.AppModule.savePath))
        self.AppModule.Settings.createReaders(self.AppModule.numReaders)
        self.AppModule.Settings.addReaderNotes()
        self.AppModule.Settings.addReaderSecondAxis()
        if self.AppModule.cellApp:
            self.AppModule.Settings.addInoculation()

    def startFunc(self):
        try:
            self.AppModule.threadStatus = self.AppModule.thread.is_alive()
        except:
            self.AppModule.threadStatus = False
        try:
            text_notification.setText("Scanning...")
            logger.info("started")
            if self.AppModule.threadStatus:
                tk.messagebox.showinfo("Error", "Test Still Running")
            else:
                self.AppModule.thread = threading.Thread(target=self.AppModule.mainLoop, args=())
                self.AppModule.thread.start()
        except:
            tk.messagebox.showinfo("Error", "Please calibrate your reader first")
            logger.exception("Failed to calibrate the reader")

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
