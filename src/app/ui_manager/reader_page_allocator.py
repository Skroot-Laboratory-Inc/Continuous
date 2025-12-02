import platform
import threading
import tkinter as tk

from src.app.authentication.helpers.decorators import requireUser
from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.model.setup_reader_form_input import SetupReaderFormInput
from src.app.reader.pump.pump_manager import PumpManager
from src.app.ui_manager.theme.gui_properties import GuiProperties
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.buttons.plus_icon_button import PlusIconButton
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.image_theme import ImageTheme
from src.app.widget.kpi_form.flow_cell.flow_cell_kpi_form import FlowCellKpiForm
from src.app.widget.pump_control_popup import PumpControlPopup
from src.app.widget.setup_form.flow_cell.flow_cell_setup_form import FlowCellSetupForm
from src.app.widget.timer import RunningTimer
from src.app.custom_exceptions.common_exceptions import UserConfirmationException
if platform.system() == "Windows":
    from src.app.reader.pump.dev_pump import DevPump as PumpClass
else:
    from src.app.reader.pump.pump import Pump as PumpClass


class ReaderPageAllocator:
    def __init__(self, rootManager: RootManager, sessionManager: SessionManager, readerPage: tk.Frame, readerNumber,
                 connectFn, calibrateFn, startFn, stopFn):
        self.connectFn = connectFn
        # TODO PumpClass and PumpManager should be provided by the context provider only if it is Flow Cell.
        self.Pump = PumpClass()
        self.PumpManager = PumpManager(self.Pump)
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.readerNumber = readerNumber
        self.calibrateFn = calibrateFn
        self.startFn = startFn
        self.stopFn = stopFn
        self.readerPage = readerPage
        self.maxReadersPerScreen = GuiProperties().readersPerScreen

        self.createButtons = []  # This is required for the plus icon to appear. It is removed from memory without it.
        self.readerFrame = self.createReaderFrames()

    def createReaderFrames(self):
        readerFrame = tk.Frame(self.readerPage, bg=Colors().body.background, padx=5, pady=5)
        readerFrame.grid_columnconfigure(0, weight=1, minsize=30)
        readerFrame.grid_columnconfigure(1, weight=9, minsize=100)
        readerFrame.grid_columnconfigure(2, weight=1, minsize=30)
        readerFrame.grid_rowconfigure(0, weight=1, minsize=30)
        readerFrame.grid_rowconfigure(1, weight=9, minsize=100)
        readerFrame.grid_rowconfigure(2, weight=1, minsize=30)
        readerFrame.place(x=0, y=0, relheight=1, relwidth=1)
        indicatorCanvas, indicator = self.createIndicator(readerFrame, Colors().status.success)
        setupReaderForm, setupFrame = self.createSetupFrame(readerFrame,
                                                            lambda: self.connectNewReader(self.readerNumber))
        header = self.createHeader(readerFrame)
        mainPlottingFrame, plottingFrame, kpiForm = self.createPlotFrame(readerFrame)
        thisReaderFrame = ReaderFrame(
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
            self.createStartButton(readerFrame, lambda: self.startReader(self.readerNumber)),
            self.createStopButton(readerFrame, lambda: self.stopReader(self.readerNumber)),
            self.createCalibrateButton(readerFrame, lambda: self.calibrateReader(self.readerNumber)),
            self.createAddReaderButton(readerFrame, lambda: self.createGuidedSetup()),
        )
        return thisReaderFrame

    @requireUser
    def createGuidedSetup(self):
        self.getReaderFrame().setupFrame.tkraise()
        self.getReaderFrame().showSetupFrame()

    def connectNewReader(self, readerNumber):
        shouldCalibrate = self.connectFn(readerNumber)
        readerFrame = self.getReaderFrame()
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
    def startReader(self, readerNumber):
        try:
            # TODO This popup should only appear if the UseCase is set to Flow Cell
            PumpControlPopup(
                self.rootManager,
                "Prime Line",
                "Would you like to prime the line?",
                self.PumpManager
            )
        except UserConfirmationException:
            return
        if self.sessionManager.user:
            self.startFn(readerNumber, self.sessionManager.getUser())
        else:
            self.startFn(readerNumber, "")
        readerFrame = self.getReaderFrame()
        readerFrame.startButton.disable()
        readerFrame.stopButton.enable()
        readerFrame.timer.resetTimer()

    @requireUser
    def stopReader(self, readerNumber):
        stopReaderThread = threading.Thread(target=self.stopFn, args=(readerNumber,), daemon=True)
        stopReaderThread.start()

    @requireUser
    def calibrateReader(self, readerNumber):
        calibrateReaderThread = threading.Thread(target=self.calibrateFn, args=(readerNumber,), daemon=True)
        calibrateReaderThread.start()

    def getIndicator(self):
        return self.getReaderFrame().indicatorCanvas, self.getReaderFrame().indicator

    def getPlottingFrame(self):
        return self.getReaderFrame().plotFrame

    def getReaderFrame(self) -> ReaderFrame:
        return self.readerFrame

    def getTimer(self) -> RunningTimer:
        return self.getReaderFrame().timer

    def createPlotFrame(self, readerFrame):
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
        # TODO Update this to use a context provider to return the KPI form based on @UseCase
        kpiForm = FlowCellKpiForm(kpiFrame, self.rootManager, self.sessionManager, self.PumpManager)
        kpiFrame.grid_remove()
        mainFrame.grid_remove()
        return mainFrame, plottingFrame, kpiForm

    def createSetupFrame(self, readerFrame, submitFn):
        setupFrame = tk.Frame(readerFrame, bg=Colors().body.background, bd=5)
        # TODO Update this to use a context provider to return the Setup Form based on @UseCase
        setupReaderForm = FlowCellSetupForm(self.rootManager, SetupReaderFormInput(), setupFrame, submitFn, self.Pump)
        setupFrame.grid(row=1, rowspan=2, column=0, columnspan=3, sticky='nsew')
        setupFrame.grid_remove()
        return setupReaderForm, setupFrame

    def createAddReaderButton(self, readerFrame, invokeFn):
        createButton = PlusIconButton(readerFrame, invokeFn)
        self.createButtons.append(createButton)
        createButton.button.grid(row=1, column=0, columnspan=3, sticky='nsew')
        createButton.show()
        return createButton

    @staticmethod
    def createIndicator(readerFrame, defaultIndicatorColor):
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
        timer = RunningTimer(readerFrame)
        timer.timer.grid(row=0, column=0, sticky='nw')
        return timer

    @staticmethod
    def createHeader(readerFrame):
        header = tk.Label(readerFrame, text="", font=FontTheme().header3,
                          background=Colors().body.background, foreground=Colors().buttons.background)
        header.grid(row=0, column=1, sticky='n')
        return header

    @staticmethod
    def createConnectButton(readerFrame, invokeFn):
        connectReadersButton = GenericButton("Connect Reader", readerFrame, invokeFn)
        connectReadersButton.button.grid(row=1, column=0, columnspan=3)
        connectReadersButton.hide()
        return connectReadersButton

    @staticmethod
    def createCalibrateButton(readerFrame, invokeFn):
        calibrateReadersButton = GenericButton("Calibrate", readerFrame, invokeFn)
        calibrateReadersButton.button.grid(row=1, column=0, columnspan=3)
        calibrateReadersButton.hide()
        return calibrateReadersButton

    @staticmethod
    def createStartButton(readerFrame, invokeFn):
        startButton = GenericButton("Start", readerFrame, invokeFn, style="Start.TButton")
        startButton.button.grid(row=2, column=0, sticky='sw')
        startButton.disable()
        return startButton

    @staticmethod
    def createStopButton(readerFrame, invokeFn):
        stopButton = GenericButton("Stop", readerFrame, invokeFn, style="Stop.TButton")
        stopButton.button.grid(row=2, column=2, sticky='se')
        stopButton.disable()
        return stopButton
