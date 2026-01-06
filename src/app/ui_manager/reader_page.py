import logging
import threading
import tkinter as tk
from typing import Callable

from reactivex.subject import BehaviorSubject

from src.app.common_modules.authentication.helpers.decorators import requireUser
from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.helper_methods.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.helper_methods.model.setup_reader_form_input import SetupReaderFormInput
from src.app.reader.interval_thread.reader_thread_manager import ReaderThreadManager
from src.app.reader.reader import Reader
from src.app.reader.sib.sib_finder import SibFinder
from src.app.use_case.use_case_factory import ContextFactory
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.buttons.plus_icon_button import PlusIconButton
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.ui_manager.progress_bar_background import ProgressBarBackground
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.image_theme import ImageTheme
from src.app.widget import text_notification
from src.app.widget.confirmation_popup import ConfirmationPopup
from src.app.widget.pump_control_popup import PumpControlPopup
from src.app.widget.timer import RunningTimer


class ReaderPage:
    """
    Manages a single reader page including UI components and business logic.
    Simplified: Combines the responsibilities of ReaderPageAllocator and ReaderPageThreadManager.
    """
    def __init__(self, frame: tk.Frame, readerNumber: int, rootManager: RootManager,
                 sessionManager: SessionManager, sibFinder: SibFinder, appendReaderFunc: Callable):
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.readerNumber = readerNumber
        self.frame = frame
        self.sibFinder = sibFinder
        self.appendReaderFunc = appendReaderFunc

        # Initialize factories and managers
        self.factory = ContextFactory()
        self.Pump = self.factory.createPump()
        self.PumpManager = self.factory.createPumpManager(self.Pump)

        # Reader state
        self.readerThreads = {}
        self.Readers = {}

        # Progress bar
        self.progressBarDisplayed = BehaviorSubject(False)
        self.progressbar = ProgressBarBackground(self.frame, self.progressBarDisplayed)

        # Create UI
        self.createButtons = []  # Keep reference to prevent garbage collection
        self.readerFrame = self._createReaderFrames()

    def _createReaderFrames(self):
        """Create the UI frame and all components for this reader."""
        readerFrame = tk.Frame(self.frame, bg=Colors().body.background, padx=5, pady=5)
        readerFrame.grid_columnconfigure(0, weight=1, minsize=30)
        readerFrame.grid_columnconfigure(1, weight=9, minsize=100)
        readerFrame.grid_columnconfigure(2, weight=1, minsize=30)
        readerFrame.grid_rowconfigure(0, weight=1, minsize=30)
        readerFrame.grid_rowconfigure(1, weight=9, minsize=100)
        readerFrame.grid_rowconfigure(2, weight=1, minsize=30)
        readerFrame.place(x=0, y=0, relheight=1, relwidth=1)

        indicatorCanvas, indicator = self._createIndicator(readerFrame, Colors().status.success)
        setupReaderForm, setupFrame = self._createSetupFrame(readerFrame,
                                                              lambda: self._connectNewReader(self.readerNumber))
        header = self._createHeader(readerFrame)
        mainPlottingFrame, plottingFrame, kpiForm = self._createPlotFrame(readerFrame)

        thisReaderFrame = ReaderFrame(
            readerFrame,
            mainPlottingFrame,
            plottingFrame,
            kpiForm,
            setupFrame,
            setupReaderForm,
            header,
            self._createTimer(readerFrame),
            indicator,
            indicatorCanvas,
            self._createStartButton(readerFrame, lambda: self._startReader(self.readerNumber)),
            self._createStopButton(readerFrame, lambda: self._stopReader(self.readerNumber)),
            self._createCalibrateButton(readerFrame, lambda: self._calibrateReader(self.readerNumber)),
            self._createAddReaderButton(readerFrame, lambda: self._createGuidedSetup()),
        )
        return thisReaderFrame

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

    def _startReaderThread(self, readerNumber, user: str):
        """Start the reader scanning thread."""
        self.appendReaderFunc(self.frame)
        self.readerThreads[readerNumber].startReaderLoop(user)

    @requireUser
    def _stopReader(self, readerNumber):
        stopReaderThread = threading.Thread(target=self._stopReaderThread, args=(readerNumber,), daemon=True)
        stopReaderThread.start()

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

    @requireUser
    def _calibrateReader(self, readerNumber):
        calibrateReaderThread = threading.Thread(target=self._calibrateReaderSync, args=(readerNumber,), daemon=True)
        calibrateReaderThread.start()

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

    # ============ UI Creation Methods ============

    def _createPlotFrame(self, readerFrame):
        """Create the plotting frame for data visualization."""
        mainFrame = tk.Frame(readerFrame, bg=Colors().body.background, bd=5)
        mainFrame.grid(row=1, column=0, columnspan=3, sticky='nsew')
        mainFrame.grid_columnconfigure(0, weight=1, uniform="plot")
        mainFrame.grid_columnconfigure(1, weight=1, uniform="plot")
        mainFrame.grid_rowconfigure(0, weight=1)
        kpiFrame = tk.Frame(mainFrame, bg=Colors().body.background)
        kpiFrame.grid(row=0, column=0, sticky='ew')
        kpiFrame.grid_columnconfigure(0, weight=1, uniform="form")
        kpiFrame.grid_columnconfigure(1, weight=1, uniform="form")
        plottingFrame = tk.Frame(mainFrame, bg=Colors().body.background, bd=5)
        plottingFrame.grid(row=0, column=1, sticky='nsew')
        kpiForm = self.factory.createKpiForm(kpiFrame, self.rootManager, self.sessionManager, self.PumpManager)
        kpiFrame.grid_remove()
        mainFrame.grid_remove()
        return mainFrame, plottingFrame, kpiForm

    def _createSetupFrame(self, readerFrame, submitFn):
        """Create the setup frame for reader configuration."""
        setupFrame = tk.Frame(readerFrame, bg=Colors().body.background, bd=5)
        config = self.factory.getSetupFormConfig()
        setupReaderForm = self.factory.createSetupForm(
            self.rootManager,
            SetupReaderFormInput(config),
            setupFrame,
            submitFn,
        )
        setupFrame.grid(row=1, rowspan=2, column=0, columnspan=3, sticky='nsew')
        setupFrame.grid_remove()
        return setupReaderForm, setupFrame

    def _createAddReaderButton(self, readerFrame, invokeFn):
        """Create the add reader button."""
        createButton = PlusIconButton(readerFrame, invokeFn)
        self.createButtons.append(createButton)
        createButton.button.grid(row=1, column=0, columnspan=3, sticky='nsew')
        createButton.show()
        return createButton

    @staticmethod
    def _createIndicator(readerFrame, defaultIndicatorColor):
        """Create the status indicator."""
        indicatorSize = ImageTheme().indicatorSize
        indicatorBorder = ImageTheme().indicatorBorder
        indicatorCanvas = tk.Canvas(
            readerFrame,
            height=indicatorSize * 2,
            width=indicatorSize * 2,
            bg=Colors().body.background,
            highlightbackground=Colors().body.background,
            bd=0)
        indicator = indicatorCanvas.create_circle(
            x=indicatorSize,
            y=indicatorSize,
            r=indicatorSize - indicatorBorder,
            fill=defaultIndicatorColor,
            outline=Colors().body.text,
            width=indicatorBorder)
        indicatorCanvas.grid(row=0, column=2, sticky='ne')
        return indicatorCanvas, indicator

    @staticmethod
    def _createTimer(readerFrame):
        """Create the timer display."""
        timer = RunningTimer(readerFrame)
        timer.timer.grid(row=0, column=0, sticky='nw')
        return timer

    @staticmethod
    def _createHeader(readerFrame):
        """Create the header label."""
        header = tk.Label(readerFrame, text="", font=FontTheme().header3,
                          background=Colors().body.background, foreground=Colors().buttons.background)
        header.grid(row=0, column=1, sticky='n')
        return header

    @staticmethod
    def _createCalibrateButton(readerFrame, invokeFn):
        """Create the calibrate button."""
        calibrateReadersButton = GenericButton("Calibrate", readerFrame, invokeFn)
        calibrateReadersButton.button.grid(row=1, column=0, columnspan=3)
        calibrateReadersButton.hide()
        return calibrateReadersButton

    @staticmethod
    def _createStartButton(readerFrame, invokeFn):
        """Create the start button."""
        startButton = GenericButton("Start", readerFrame, invokeFn, style="Start.TButton")
        startButton.button.grid(row=2, column=0, sticky='sw')
        startButton.disable()
        return startButton

    @staticmethod
    def _createStopButton(readerFrame, invokeFn):
        """Create the stop button."""
        stopButton = GenericButton("Stop", readerFrame, invokeFn, style="Stop.TButton")
        stopButton.button.grid(row=2, column=2, sticky='se')
        stopButton.disable()
        return stopButton
