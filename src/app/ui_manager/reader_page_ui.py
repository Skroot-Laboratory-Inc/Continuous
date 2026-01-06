import tkinter as tk

from src.app.helper_methods.model.setup_reader_form_input import SetupReaderFormInput
from src.app.use_case.use_case_factory import ContextFactory
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.buttons.plus_icon_button import PlusIconButton
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.image_theme import ImageTheme
from src.app.widget.timer import RunningTimer


class ReaderPageUI:
    """
    Handles UI component creation for a reader page.
    Separated from business logic for better organization and readability.
    """

    def __init__(self, rootManager: RootManager, sessionManager, pumpManager):
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.pumpManager = pumpManager
        self.factory = ContextFactory()

    def createReaderFrame(self, parentFrame, readerNumber, connectFn, startFn, stopFn, calibrateFn, setupFn):
        """Create the complete reader frame with all UI components."""
        readerFrame = tk.Frame(parentFrame, bg=Colors().body.background, padx=5, pady=5)
        readerFrame.grid_columnconfigure(0, weight=1, minsize=30)
        readerFrame.grid_columnconfigure(1, weight=9, minsize=100)
        readerFrame.grid_columnconfigure(2, weight=1, minsize=30)
        readerFrame.grid_rowconfigure(0, weight=1, minsize=30)
        readerFrame.grid_rowconfigure(1, weight=9, minsize=100)
        readerFrame.grid_rowconfigure(2, weight=1, minsize=30)
        readerFrame.place(x=0, y=0, relheight=1, relwidth=1)

        indicatorCanvas, indicator = self.createIndicator(readerFrame, Colors().status.success)
        setupReaderForm, setupFrame = self.createSetupFrame(readerFrame, connectFn)
        header = self.createHeader(readerFrame)
        mainPlottingFrame, plottingFrame, kpiForm = self.createPlotFrame(readerFrame)

        return ReaderFrame(
            readerFrame,
            mainPlottingFrame,
            plottingFrame,
            kpiForm,
            setupFrame,
            setupReaderForm,
            header,
            self.createTimer(readerFrame),
            indicator,
            indicatorCanvas,
            self.createStartButton(readerFrame, startFn),
            self.createStopButton(readerFrame, stopFn),
            self.createCalibrateButton(readerFrame, calibrateFn),
            self.createAddReaderButton(readerFrame, setupFn),
        )

    def createPlotFrame(self, readerFrame):
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

        kpiForm = self.factory.createKpiForm(kpiFrame, self.rootManager, self.sessionManager, self.pumpManager)
        kpiFrame.grid_remove()
        mainFrame.grid_remove()

        return mainFrame, plottingFrame, kpiForm

    def createSetupFrame(self, readerFrame, submitFn):
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

    @staticmethod
    def createAddReaderButton(readerFrame, invokeFn):
        """Create the add reader button."""
        createButton = PlusIconButton(readerFrame, invokeFn)
        createButton.button.grid(row=1, column=0, columnspan=3, sticky='nsew')
        createButton.show()
        return createButton

    @staticmethod
    def createIndicator(readerFrame, defaultIndicatorColor):
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
    def createTimer(readerFrame):
        """Create the timer display."""
        timer = RunningTimer(readerFrame)
        timer.timer.grid(row=0, column=0, sticky='nw')
        return timer

    @staticmethod
    def createHeader(readerFrame):
        """Create the header label."""
        header = tk.Label(readerFrame, text="", font=FontTheme().header3,
                          background=Colors().body.background, foreground=Colors().buttons.background)
        header.grid(row=0, column=1, sticky='n')
        return header

    @staticmethod
    def createCalibrateButton(readerFrame, invokeFn):
        """Create the calibrate button."""
        calibrateButton = GenericButton("Calibrate", readerFrame, invokeFn)
        calibrateButton.button.grid(row=1, column=0, columnspan=3)
        calibrateButton.hide()
        return calibrateButton

    @staticmethod
    def createStartButton(readerFrame, invokeFn):
        """Create the start button."""
        startButton = GenericButton("Start", readerFrame, invokeFn, style="Start.TButton")
        startButton.button.grid(row=2, column=0, sticky='sw')
        startButton.disable()
        return startButton

    @staticmethod
    def createStopButton(readerFrame, invokeFn):
        """Create the stop button."""
        stopButton = GenericButton("Stop", readerFrame, invokeFn, style="Stop.TButton")
        stopButton.button.grid(row=2, column=2, sticky='se')
        stopButton.disable()
        return stopButton
