import threading
import tkinter as tk

from src.app.authentication.authentication_popup import AuthenticationPopup
from src.app.buttons.generic_button import GenericButton
from src.app.buttons.plus_icon_button import PlusIconButton
from src.app.model.setup_reader_form_input import SetupReaderFormInput
from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.harvest_text import HarvestText
from src.app.widget.setup_reader_form import SetupReaderForm
from src.app.widget.timer import RunningTimer


class ReaderPageAllocator:
    def __init__(self, rootManager: RootManager, readerPage: tk.Frame, readerNumber, connectFn, calibrateFn, startFn, stopFn):
        self.connectFn = connectFn
        self.RootManager = rootManager
        self.readerNumber = readerNumber
        self.calibrateFn = calibrateFn
        self.startFn = startFn
        self.stopFn = stopFn
        self.readerPage = readerPage
        self.maxReadersPerScreen = GuiProperties().readersPerScreen
        self.Colors = Colors()
        self.createButtons = []  # This is required for the plus icon to appear. It is removed from memory without it.
        self.readerFrame = self.createReaderFrames()

    def createReaderFrames(self):
        readerFrame = tk.Frame(self.readerPage, bg=self.Colors.secondaryColor, padx=5, pady=5)
        readerFrame.grid_columnconfigure(0, weight=1, minsize=30)
        readerFrame.grid_columnconfigure(1, weight=9, minsize=490)
        readerFrame.grid_columnconfigure(2, weight=1, minsize=30)
        readerFrame.grid_rowconfigure(0, weight=1, minsize=30)
        readerFrame.grid_rowconfigure(1, weight=9, minsize=290)
        readerFrame.grid_rowconfigure(2, weight=1, minsize=30)
        readerFrame.grid(row=0, column=0, sticky='nsew')
        indicatorCanvas, indicator = self.createIndicator(readerFrame, 'green')
        setupReaderForm, setupFrame = self.createSetupFrame(readerFrame, lambda: self.connectNewReader(self.readerNumber))
        header = self.createHeader(readerFrame, self.readerNumber, setupReaderForm.lotIdEntry.get())
        mainPlottingFrame, plottingFrame, harvestText = self.createPlotFrame(readerFrame)
        thisReaderFrame = ReaderFrame(
            readerFrame,
            mainPlottingFrame,
            plottingFrame,
            harvestText,
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

    def createGuidedSetup(self):
        self.getReaderFrame().setupFrame.tkraise()
        self.getReaderFrame().showSetupFrame()

    def connectNewReader(self, readerNumber):
        shouldCalibrate = self.connectFn(readerNumber)
        readerFrame = self.getReaderFrame()
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

    def startReader(self, readerNumber):
        if AuthenticationPopup(self.RootManager).isAuthenticated:
            self.startFn(readerNumber)
            readerFrame = self.getReaderFrame()
            readerFrame.startButton.disable()
            readerFrame.stopButton.enable()
            readerFrame.timer.resetTimer()

    def stopReader(self, readerNumber):
        if AuthenticationPopup(self.RootManager).isAuthenticated:
            stopReaderThread = threading.Thread(target=self.stopFn, args=(readerNumber,), daemon=True)
            stopReaderThread.start()

    def calibrateReader(self, readerNumber):
        if AuthenticationPopup(self.RootManager).isAuthenticated:
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
        mainFrame = tk.Frame(readerFrame, bg=self.Colors.secondaryColor, bd=5)
        mainFrame.grid(row=1, column=0, columnspan=3)
        mainFrame.grid_rowconfigure(0, weight=9, minsize=265)
        mainFrame.grid_rowconfigure(1, weight=1, minsize=35)
        plottingFrame = tk.Frame(mainFrame, bg=self.Colors.secondaryColor, bd=5)
        plottingFrame.grid(row=0, column=0, sticky='nsew')
        harvestText = HarvestText(mainFrame)
        harvestText.text.grid(row=1, column=0)
        mainFrame.grid_remove()
        return mainFrame, plottingFrame, harvestText

    def createSetupFrame(self, readerFrame, submitFn):
        setupFrame = tk.Frame(readerFrame, bg=self.Colors.secondaryColor, bd=5)
        setupReaderForm = SetupReaderForm(SetupReaderFormInput(), setupFrame, submitFn)
        setupFrame.grid(row=1, column=0, columnspan=3, sticky='nsew')
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
        indicatorCanvas = tk.Canvas(
            readerFrame,
            height=34,
            width=34,
            bg="white",
            highlightbackground="white",
            bd=0)
        indicator = indicatorCanvas.create_circle(
                x=17, y=17, r=15, fill=defaultIndicatorColor, outline="black", width=2)
        indicatorCanvas.grid(row=0, column=2, sticky='ne')
        return indicatorCanvas, indicator

    @staticmethod
    def createTimer(readerFrame):
        timer = RunningTimer(readerFrame)
        timer.timer.grid(row=0, column=0, sticky='nw')
        return timer

    @staticmethod
    def createHeader(readerFrame, readerNumber, lotId):
        header = tk.Label(readerFrame, text=f"Reader {readerNumber}: {lotId}", font=FontTheme().header3, background=Colors().secondaryColor, foreground=Colors().primaryColor)
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
        startButton = GenericButton("Start", readerFrame, invokeFn)
        startButton.button.grid(row=2, column=0, sticky='sw')
        startButton.disable()
        return startButton

    @staticmethod
    def createStopButton(readerFrame, invokeFn):
        stopButton = GenericButton("Stop", readerFrame, invokeFn)
        stopButton.button.grid(row=2, column=2, sticky='se')
        stopButton.disable()
        return stopButton
