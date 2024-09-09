import logging
import threading
import time
import tkinter as tk
from tkinter import messagebox

from src.app.buttons.calibrate_readers import CalibrateReadersButton
from src.app.buttons.connect_readers import ConnectReadersButton
from src.app.buttons.guided_setup_button import GuidedSetupButton
from src.app.buttons.help_button import HelpButton
from src.app.buttons.start_button import StartButton
from src.app.buttons.stop_button import StopButton
from src.app.exception.common_exceptions import UserExitedException
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.properties.gui_properties import GuiProperties
from src.app.reader.sib.sib import Sib
from src.app.reader.sib.sib_interface import SibInterface
from src.app.ui_manager.root_event_manager import UPDATE_ISSUES
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification
from src.app.widget.issues.issue_log import IssueLog


class ButtonFunctions:
    def __init__(self, AppModule, rootManager: RootManager, PortAllocator):
        self.RootManager = rootManager
        self.MainThreadManager = None  # To be filled in later.
        self.AppModule = AppModule
        self.SibInterfaces = []
        self.PortAllocator = PortAllocator
        self.calibrateSynchronously = False

    def createGuidedSetupButton(self, master):
        self.GuidedSetupButton = GuidedSetupButton(master, self.AppModule.guidedSetup)

    def createButtonsOnNewFrame(self):
        self.StartButton = StartButton(self.RootManager.getRoot(), self.startFunc)
        self.StopButton = StopButton(self.AppModule.bodyFrame, self.stopFunc)
        self.HelpButton = HelpButton(self.RootManager, self.AppModule)

    def startFunc(self):
        guiProperties = GuiProperties()
        self.MainThreadManager.summaryFrame.place(
            relx=0.67,
            rely=guiProperties.bodyRelY + guiProperties.bodyHeight / 2,
            relwidth=0.33,
            relheight=guiProperties.bodyHeight / 2)
        self.StartButton.destroySelf()
        self.AppModule.bodyFrame.tkraise()
        self.AppModule.Settings.createReaders(self.AppModule.guidedSetupForm.getNumReaders(), self.SibInterfaces)
        self.AppModule.Settings.addReaderNotes()
        self.AppModule.Settings.addReaderSecondAxis()
        # self.AppModule.Settings.addInoculation()
        self.StopButton.place()
        self.AppModule.IssueLog.placeIssueLog()
        self.RootManager.generateEvent(UPDATE_ISSUES)
        self.MainThreadManager.Timer.createWidget(self.AppModule.bodyFrame)
        text_notification.setText("Scanning...")
        logging.info("started")
        self.MainThreadManager.startReaderLoop(self.AppModule.Readers)

    def stopFunc(self):
        endExperiment = tk.messagebox.askquestion('End Experiment', 'Are you sure you wish to end the experiment?')
        if endExperiment == 'yes':
            logging.info('Experiment ended by user.')
            try:
                self.MainThreadManager.thread.shutdown_flag.set()
            except:
                text_notification.setText("Experiment Ended.", ('Courier', 9, 'bold'), self.AppModule.primaryColor,
                                          self.AppModule.secondaryColor)
                self.AppModule.resetRun()
            self.StopButton.destroySelf()
            text_notification.setText("Ending experiment once current sweep is complete.", ('Courier', 9, 'bold'),
                                      self.AppModule.primaryColor, self.AppModule.secondaryColor)

    def findReaders(self, numReaders, globalFileManager):
        logging.info(f'calibrate button pressed')
        for readerNumber in range(1, numReaders + 1):
            try:
                port = self.findPort(readerNumber)
                self.SibInterfaces.append(instantiateReader(port, self.PortAllocator, readerNumber, True, globalFileManager))
            except UserExitedException:
                self.RootManager.destroyRoot()
                logging.exception("User exited during port finding.")
                raise
            except:
                logging.exception(f'Failed to instantiate reader {readerNumber}')

    def calibrateReaders(self):
        self.CalibrateReadersButton.destroySelf()
        calibrateReadersThread = threading.Thread(target=self.calibrateAllReaders, daemon=True)
        calibrateReadersThread.start()

    def calibrateAllReaders(self):
        text_notification.setText("Calibrating readers... do not move them", ('Courier', 9, 'bold'),
                                  self.AppModule.primaryColor, self.AppModule.secondaryColor)
        threads = self.startSibCalibrationThread(self.AppModule.guidedSetupForm.getNumReaders())
        for t in threads:
            t.join()
        calibrationFailed = False
        readersCalibrationFailed = ""
        for SibInterface in self.SibInterfaces:
            if SibInterface.calibrationFailed:
                calibrationFailed = True
                text_notification.setText(f"Calibration failed for reader {SibInterface.readerNumber}",
                                          ('Courier', 9, 'bold'), self.AppModule.primaryColor,
                                          self.AppModule.secondaryColor)
                readersCalibrationFailed = readersCalibrationFailed.join(f" {SibInterface.readerNumber}")
        if calibrationFailed:
            text_notification.setText(f"Calibration failed for readers:{readersCalibrationFailed}",
                                      ('Courier', 9, 'bold'),
                                      self.AppModule.primaryColor, self.AppModule.secondaryColor)
            self.StopButton.place()
        else:
            text_notification.setText(f"Calibration Complete", ('Courier', 9, 'bold'),
                                      self.AppModule.primaryColor, self.AppModule.secondaryColor)
            self.StartButton.place()

    def startSibCalibrationThread(self, numReaders):
        calThreads = []
        for readerIndex in range(numReaders):
            if self.calibrateSynchronously:
                calThread = threading.Thread(target=self.performSibCalibration, args=(readerIndex,), daemon=True)
                calThreads.append(calThread)
                calThread.start()
            else:
                self.performSibCalibration(readerIndex)
        return calThreads

    def performSibCalibration(self, readerIndex):
        try:
            logging.info(f"Calibrating reader {readerIndex + 1}")
            self.SibInterfaces[readerIndex].calibrateIfRequired()
            logging.info(f"Calibration complete for reader {readerIndex + 1}")
            self.SibInterfaces[readerIndex].loadCalibrationFile()
        except:
            self.SibInterfaces[readerIndex].calibrationFailed = True
            logging.exception(f'Failed to calibrate reader {readerIndex + 1}')

    def connectReaders(self, numReaders, globalFileManager):
        self.ConnectReadersButton.destroySelf()
        for readerNumber in range(1, numReaders + 1):
            try:
                port = self.findPort(readerNumber)
                self.SibInterfaces.append(
                    instantiateReader(port, self.PortAllocator, readerNumber, False, globalFileManager),
                )
            except UserExitedException:
                self.RootManager.destroyRoot()
                logging.exception("User exited during port finding.")
                raise
        self.AppModule.foundPorts = True
        self.StartButton.place()

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
                        messagebox.showerror(
                            f'Reader {readerNumber}',
                            f'Reader {readerNumber}\nNew Reader not found more than 3 times,\nApp Restart required.')
                        break
                    else:
                        shouldContinue = messagebox.askokcancel(
                            f'Reader {readerNumber}',
                            f'Reader {readerNumber}\nNew Reader not found, ensure a new Reader is plugged in, then press OK\n'
                            f'Press cancel to shutdown the app.')
                        if not shouldContinue:
                            break
            raise UserExitedException("The user chose not to go forward during port finding.")
        else:
            return '', ''

    def placeConnectReadersButton(self):
        self.ConnectReadersButton = ConnectReadersButton(
            self.AppModule.bodyFrame,
            self.connectReaders,
            self.AppModule.guidedSetupForm.getNumReaders(),
            self.AppModule.GlobalFileManager,
        )
        self.ConnectReadersButton.place()

    def placeCalibrateReadersButton(self):
        self.CalibrateReadersButton = CalibrateReadersButton(self.AppModule.bodyFrame, self.calibrateReaders)
        self.CalibrateReadersButton.place()


def pauseUntilUserClicks(readerNumber):
    messagebox.showinfo(f'Reader {readerNumber}',
                           f'Reader {readerNumber}\nPress OK when reader {readerNumber} is plugged in')


def instantiateReader(port, PortAllocator, readerNumber, calibrationRequired, globalFileManager) -> SibInterface:
    try:
        sib = Sib(
            port,
            ReaderFileManager(globalFileManager, readerNumber).getCalibrationGlobalLocation(),
            readerNumber,
            PortAllocator,
            calibrationRequired,
        )
        success = sib.performHandshake()
        if success:
            return sib
        else:
            logging.info(f"Failed to handshake SIB #{readerNumber} on port {port}")
            text_notification.setText("Failed to connect to SiB")
            sib.close()
    except:
        logging.exception(f"Failed to instantiate reader {readerNumber}")
