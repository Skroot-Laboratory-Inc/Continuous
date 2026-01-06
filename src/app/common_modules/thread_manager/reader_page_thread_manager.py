import logging
from typing import Callable

from reactivex import Subject
from reactivex.subject import BehaviorSubject

from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.helper_methods.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.reader.interval_thread.reader_thread_manager import ReaderThreadManager
from src.app.reader.reader import Reader
from src.app.reader.sib.sib_finder import SibFinder
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.ui_manager.progress_bar_background import ProgressBarBackground
from src.app.ui_manager.reader_page_allocator import ReaderPageAllocator
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification
from src.app.widget.confirmation_popup import ConfirmationPopup
from src.app.widget.pump_control_popup import PumpControlPopup


class ReaderPageThreadManager:
    """
    Manages the reader thread and UI for a single reader page.
    Simplified: Each page contains exactly one reader.
    """
    def __init__(self, readerPage, startingReaderNumber, rootManager: RootManager, sessionManager: SessionManager, sibFinder: SibFinder, appendReaderFunc: Callable):
        self.readerAllocator = ReaderPageAllocator(
            rootManager,
            sessionManager,
            readerPage,
            startingReaderNumber,
            self.connectReader,
            self.calibrateReader,
            self.startReaderThread,
            self.stopReaderThread,
        )
        self.readerPage = readerPage
        self.progressBarDisplayed = BehaviorSubject(False)
        self.progressbar = ProgressBarBackground(self.readerPage, self.progressBarDisplayed)
        self.appendReaderFunc = appendReaderFunc
        self.readerThreads = {}
        self.Readers = {}
        self.RootManager = rootManager
        self.sessionManager = sessionManager
        self.SibFinder = sibFinder

    def startProgressBar(self, duration, hideBar: Subject):
        self.progressBarDisplayed.on_next(True)
        self.progressbar.progressbar.start(duration, hideBar, lambda: self.progressBarDisplayed.on_next(False))

    def connectReader(self, readerNumber):
        try:
            guidedSetupForm, globalFileManager = self.readerAllocator.getReaderFrame().setupReaderForm.getConfiguration()
            sib = self.SibFinder.connectSib(readerNumber)
            self.Readers[readerNumber] = Reader(
                globalFileManager,
                readerNumber,
                self.readerAllocator,
                sib,
            )
            self.readerThreads[readerNumber] = ReaderThreadManager(
                self.Readers[readerNumber],
                self.RootManager,
                guidedSetupForm,
                self.resetReader,
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

    def issueOccurred(self):
        """Check if any reader thread has current issues."""
        for readerThread in self.readerThreads.values():
            if readerThread.currentIssues != {}:
                return True
        return False

    def calibrateReader(self, readerNumber):
        sib = self.Readers[readerNumber].SibInterface
        readerFrame = self.readerAllocator.getReaderFrame()
        readerFrame.calibrateButton.disable()
        text_notification.setText("Calibration started.")
        self.startProgressBar(sib.estimateDuration(), sib.getCurrentlyScanning())
        calibrationSuccessful = sib.performCalibration()
        if calibrationSuccessful:
            text_notification.setText(f"Calibration complete.")
            readerFrame.calibrateButton.hide()
            readerFrame.startButton.enable()
            readerFrame.showPlotFrame()
        else:
            text_notification.setText(f"Failed to perform calibration, Reader hardware disconnected.\nPlease contact your system administrator.")
            readerFrame.calibrateButton.enable()

    def startReaderThread(self, readerNumber, user: str):
        self.appendReaderFunc(self.readerPage)
        self.readerThreads[readerNumber].startReaderLoop(user)

    def getReader(self, readerNumber) -> Reader:
        return self.Readers[readerNumber]

    def getReaderPageFrame(self) -> ReaderFrame:
        return self.readerAllocator.readerFrame

    def resetReader(self, readerNumber):
        self.getReader(readerNumber).SibInterface.close()
        self.getReader(readerNumber).Indicator.changeIndicatorGreen()
        for widgets in self.getReaderPageFrame().plotFrame.winfo_children():
            widgets.destroy()

    def stopReaderThread(self, readerNumber):
        try:
            ConfirmationPopup(
                self.RootManager,
                f'Stop Vessel #{readerNumber}',
                f'Are you sure you wish to stop vessel {readerNumber}?',
            )
            logging.info('Experiment ended by user.', extra={"id": f"Reader {readerNumber}"})
            readerFrame = self.readerAllocator.getReaderFrame()
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
            if self.readerAllocator.factory.showPumpControls():
                PumpControlPopup(
                    self.RootManager,
                    "Clear Line",
                    "Would you like to clear the line?",
                    self.readerAllocator.PumpManager,
                    altCancelText="Close",
                    requireConfirmation=False
                )
        except UserConfirmationException:
            return False
