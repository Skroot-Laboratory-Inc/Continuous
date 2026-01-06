import logging
import threading
import tkinter as tk
from typing import Callable

from reactivex.subject import BehaviorSubject

from src.app.common_modules.authentication.helpers.decorators import requireUser
from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.helper_methods.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.reader.interval_thread.reader_thread_manager import ReaderThreadManager
from src.app.reader.reader import Reader
from src.app.reader.sib.sib_finder import SibFinder
from src.app.use_case.use_case_factory import ContextFactory
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.ui_manager.progress_bar_background import ProgressBarBackground
from src.app.ui_manager.reader_page_ui import ReaderPageUI
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification
from src.app.widget.confirmation_popup import ConfirmationPopup
from src.app.widget.pump_control_popup import PumpControlPopup
from src.app.widget.timer import RunningTimer


class ReaderPage:
    """
    Manages business logic and state for a single reader page.
    UI creation is delegated to ReaderPageUI for better separation of concerns.
    """
    def __init__(self, frame: tk.Frame, readerNumber: int, rootManager: RootManager,
                 sessionManager: SessionManager, sibFinder: SibFinder, appendReaderFunc: Callable):
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.readerNumber = readerNumber
        self.frame = frame
        self.sibFinder = sibFinder
        self.appendReaderFunc = appendReaderFunc
        self.factory = ContextFactory()
        self.Pump = self.factory.createPump()
        self.PumpManager = self.factory.createPumpManager(self.Pump)
        self.readerThreads = {}
        self.Readers = {}
        self.progressBarDisplayed = BehaviorSubject(False)
        self.progressbar = ProgressBarBackground(self.frame, self.progressBarDisplayed)
        self.ui = ReaderPageUI(rootManager, sessionManager, self.PumpManager)
        self.readerFrame = self._createReaderFrame()

    def _createReaderFrame(self):
        """Create the UI frame and all components for this reader."""
        return self.ui.createReaderFrame(
            self.frame,
            self.readerNumber,
            lambda: self._connectNewReader(self.readerNumber),
            lambda: self._startReader(self.readerNumber),
            lambda: self._stopReader(self.readerNumber),
            lambda: self._calibrateReader(self.readerNumber),
            lambda: self._createGuidedSetup(),
        )

    # ============ Public API Methods ============

    def getReaderFrame(self) -> ReaderFrame:
        return self.readerFrame

    def getTimer(self) -> RunningTimer:
        return self.readerFrame.timer

    def getIndicator(self):
        return self.readerFrame.indicatorCanvas, self.readerFrame.indicator

    def getPlottingFrame(self):
        return self.readerFrame.plotFrame

    def getReader(self, readerNumber) -> Reader:
        return self.Readers[readerNumber]

    def getReaderPageFrame(self) -> ReaderFrame:
        return self.readerFrame

    def issueOccurred(self):
        """Check if any reader thread has current issues."""
        for readerThread in self.readerThreads.values():
            if readerThread.currentIssues != {}:
                return True
        return False

    # ============ Reader Management Methods ============

    @requireUser
    def _createGuidedSetup(self):
        self.readerFrame.setupFrame.tkraise()
        self.readerFrame.showSetupFrame()

    def _connectNewReader(self, readerNumber):
        shouldCalibrate = self._connectReader(readerNumber)
        readerFrame = self.readerFrame
        readerFrame.updateHeader()
        if shouldCalibrate is None:
            pass  # This means that it failed to find the reader.
        elif shouldCalibrate:
            readerFrame.createButton.hide()
            readerFrame.calibrateButton.show()
            readerFrame.calibrateButton.button.tkraise()
        else:
            readerFrame.createButton.hide()
            readerFrame.startButton.enable()
            readerFrame.showPlotFrame()

    @requireUser
    def _startReader(self, readerNumber):
        try:
            if self.factory.showPumpControls():
                PumpControlPopup(
                    self.rootManager,
                    "Prime Line",
                    "Would you like to prime the line?",
                    self.PumpManager
                )
        except UserConfirmationException:
            return
        if self.sessionManager.user:
            self._startReaderThread(readerNumber, self.sessionManager.getUser())
        else:
            self._startReaderThread(readerNumber, "")
        readerFrame = self.readerFrame
        readerFrame.startButton.disable()
        readerFrame.stopButton.enable()
        readerFrame.timer.resetTimer()

    @requireUser
    def _stopReader(self, readerNumber):
        stopReaderThread = threading.Thread(target=self._stopReaderThread, args=(readerNumber,), daemon=True)
        stopReaderThread.start()

    @requireUser
    def _calibrateReader(self, readerNumber):
        calibrateReaderThread = threading.Thread(target=self._calibrateReaderSync, args=(readerNumber,), daemon=True)
        calibrateReaderThread.start()

    def _connectReader(self, readerNumber):
        """Connect to the reader hardware and initialize."""
        try:
            guidedSetupForm, globalFileManager = self.readerFrame.setupReaderForm.getConfiguration()
            sib = self.sibFinder.connectSib(readerNumber)
            self.Readers[readerNumber] = Reader(
                globalFileManager,
                readerNumber,
                self,
                sib,
            )
            self.readerThreads[readerNumber] = ReaderThreadManager(
                self.Readers[readerNumber],
                self.rootManager,
                guidedSetupForm,
                self._resetReader,
                self.issueOccurred,
            )
            if sib.getCalibrationFilePresent().value:
                return guidedSetupForm.getCalibrate()
            else:
                text_notification.setText("No calibration found. Please calibrate the reader.")
                return True
        except UserConfirmationException:
            return None
        except:
            logging.exception("Failed to connect new reader.", extra={"id": f"Reader {readerNumber}"})
            text_notification.setText("Reader hardware disconnected.\nPlease contact your system administrator.")
            return None

    def _startReaderThread(self, readerNumber, user: str):
        """Start the reader scanning thread."""
        self.appendReaderFunc(self.frame)
        self.readerThreads[readerNumber].startReaderLoop(user)

    def _stopReaderThread(self, readerNumber):
        """Stop the reader scanning thread."""
        try:
            ConfirmationPopup(
                self.rootManager,
                f'Stop Vessel #{readerNumber}',
                f'Are you sure you wish to stop vessel {readerNumber}?',
            )
            logging.info('Experiment ended by user.', extra={"id": f"Reader {readerNumber}"})
            readerFrame = self.readerFrame
            readerFrame.stopButton.disable()
            text_notification.setText(
                f"Stopped scanning. Please wait for current sweep to complete to reset it."
            )
            self.readerThreads[readerNumber].thread.shutdown_flag.set()
            self.readerThreads[readerNumber].thread.join()
            readerFrame.hidePlotFrame()
            readerFrame.createButton.show()
            readerFrame.resetSetupForm()
            readerFrame.timer.resetTimer()
            readerFrame.kpiForm.resetForm()
            if self.factory.showPumpControls():
                PumpControlPopup(
                    self.rootManager,
                    "Clear Line",
                    "Would you like to clear the line?",
                    self.PumpManager,
                    altCancelText="Close",
                    requireConfirmation=False
                )
        except UserConfirmationException:
            return False

    def _calibrateReaderSync(self, readerNumber):
        """Calibrate the reader."""
        sib = self.Readers[readerNumber].SibInterface
        readerFrame = self.readerFrame
        readerFrame.calibrateButton.disable()
        text_notification.setText("Calibration started.")
        self._startProgressBar(sib.estimateDuration(), sib.getCurrentlyScanning())
        calibrationSuccessful = sib.performCalibration()
        if calibrationSuccessful:
            text_notification.setText(f"Calibration complete.")
            readerFrame.calibrateButton.hide()
            readerFrame.startButton.enable()
            readerFrame.showPlotFrame()
        else:
            text_notification.setText(f"Failed to perform calibration, Reader hardware disconnected.\nPlease contact your system administrator.")
            readerFrame.calibrateButton.enable()

    def _resetReader(self, readerNumber):
        """Reset the reader after stopping."""
        self.getReader(readerNumber).SibInterface.close()
        self.getReader(readerNumber).Indicator.changeIndicatorGreen()
        for widgets in self.readerFrame.plotFrame.winfo_children():
            widgets.destroy()

    def _startProgressBar(self, duration, hideBar):
        """Start the progress bar."""
        self.progressBarDisplayed.on_next(True)
        self.progressbar.progressbar.start(duration, hideBar, lambda: self.progressBarDisplayed.on_next(False))
