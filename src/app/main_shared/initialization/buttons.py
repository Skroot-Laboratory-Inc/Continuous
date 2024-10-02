import logging
import threading
import tkinter as tk
from tkinter import messagebox

from src.app.buttons.guided_setup_button import GuidedSetupButton
from src.app.properties.gui_properties import GuiProperties
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification


class ButtonFunctions:
    def __init__(self, AppModule, rootManager: RootManager):
        self.RootManager = rootManager
        self.MainThreadManager = None  # To be filled in later.
        self.AppModule = AppModule
        self.SibInterfaces = []
        self.calibrateSynchronously = False

    def stopFunc(self):
        endExperiment = tk.messagebox.askquestion('End Experiment', 'Are you sure you wish to end the experiment?')
        if endExperiment == 'yes':
            logging.info('Experiment ended by user.')
            try:
                self.MainThreadManager.thread.shutdown_flag.set()
            except:
                text_notification.setText("Experiment Ended.", ('Courier', 9, 'bold'))
                self.AppModule.resetRun()
            self.StopButton.destroySelf()
            text_notification.setText("Ending experiment once current sweep is complete.", ('Courier', 9, 'bold'))

    def calibrateReaders(self):
        self.CalibrateReadersButton.destroySelf()
        calibrateReadersThread = threading.Thread(target=self.calibrateAllReaders, daemon=True)
        calibrateReadersThread.start()

    def calibrateAllReaders(self):
        text_notification.setText("Calibrating readers... do not move them", ('Courier', 9, 'bold'))
        threads = self.startSibCalibrationThread(self.AppModule.guidedSetupForm.getNumReaders())
        for t in threads:
            t.join()
        calibrationFailed = False
        readersCalibrationFailed = ""
        for SibInterface in self.SibInterfaces:
            if SibInterface.calibrationFailed:
                calibrationFailed = True
                text_notification.setText(
                    f"Calibration failed for reader {SibInterface.readerNumber}",
                    ('Courier', 9, 'bold'),
                )
                readersCalibrationFailed = readersCalibrationFailed.join(f" {SibInterface.readerNumber}")
        if calibrationFailed:
            text_notification.setText(
                f"Calibration failed for readers:{readersCalibrationFailed}",
                ('Courier', 9, 'bold'),
            )
            self.StopButton.place()
        else:
            text_notification.setText(f"Calibration Complete", ('Courier', 9, 'bold'))
            self.StartButton.place()

    def startSibCalibrationThread(self, readerIndex):
        calThread = threading.Thread(target=self.performSibCalibration, args=(readerIndex,), daemon=True)
        calThread.start()
        return calThread

    def performSibCalibration(self, readerIndex):
        try:
            logging.info(f"Calibrating reader {readerIndex + 1}")
            self.SibInterfaces[readerIndex].calibrateIfRequired()
            logging.info(f"Calibration complete for reader {readerIndex + 1}")
            self.SibInterfaces[readerIndex].loadCalibrationFile()
        except:
            self.SibInterfaces[readerIndex].calibrationFailed = True
            logging.exception(f'Failed to calibrate reader {readerIndex + 1}')
