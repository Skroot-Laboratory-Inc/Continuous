import threading
import tkinter as tk

from src.app.buttons.calibrate_readers import CalibrateReaderButton
from src.app.buttons.connect_reader import ConnectReaderButton
from src.app.buttons.plus_icon_button import PlusIconButton
from src.app.buttons.start_button import StartButton
from src.app.buttons.stop_button import StopButton
from src.app.model.setup_reader_form_input import SetupReaderFormInput
from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.widget.setup_reader_form import SetupReaderForm
from src.app.widget.timer import RunningTimer


class ReaderPageAllocator:
    def __init__(self, readerPage: tk.Frame, startingReaderNumber, finalReaderNumber, connectFn, calibrateFn, startFn, stopFn):
        self.connectFn = connectFn
        self.calibrateFn = calibrateFn
        self.startFn = startFn
        self.stopFn = stopFn
        self.readerPage = readerPage
        self.maxReadersPerScreen = GuiProperties().readersPerScreen
        self.startingReaderNumber = startingReaderNumber
        self.finalReaderNumber = finalReaderNumber
        self.Colors = Colors()
        self.createButtons = []  # This is required for the plus icon to appear. It is removed from memory without it.
        self.readerFrames = {}
        self.positions = {
            0: {"row": 0, "column": 0},
            1: {"row": 0, "column": 1},
            2: {"row": 1, "column": 0},
            3: {"row": 1, "column": 1}
        }
        self.createReaderFrames()

    def createReaderFrames(self):
        for readerNumber in range(self.startingReaderNumber, self.finalReaderNumber):
            position = (readerNumber-1) % self.maxReadersPerScreen

            readerFrame = tk.Frame(self.readerPage, bg=self.Colors.secondaryColor, highlightbackground="light grey", highlightthickness=2, padx=5, pady=5)
            readerFrame.grid_columnconfigure(0, weight=1, minsize=35)
            readerFrame.grid_columnconfigure(1, weight=9, minsize=300)
            readerFrame.grid_columnconfigure(2, weight=1, minsize=35)
            readerFrame.grid_rowconfigure(0, weight=1, minsize=35)
            readerFrame.grid_rowconfigure(1, weight=9, minsize=300)
            readerFrame.grid_rowconfigure(2, weight=1, minsize=40)
            readerFrame.grid(
                row=self.positions[position]["row"],
                column=self.positions[position]["column"],
                sticky='nesw')
            self.createHeader(readerFrame, readerNumber)
            indicatorCanvas, indicator = self.createIndicator(readerFrame, 'green')
            configuration, setupFrame = self.createSetupFrame(readerFrame, lambda num=readerNumber: self.connectNewReader(num))
            self.readerFrames[readerNumber] = ReaderFrame(
                readerFrame,
                self.createPlotFrame(readerFrame),
                setupFrame,
                configuration,
                self.createTimer(readerFrame),
                indicator,
                indicatorCanvas,
                self.createStartButton(readerFrame, lambda num=readerNumber: self.startReader(num)),
                self.createStopButton(readerFrame, lambda num=readerNumber: self.stopReader(num)),
                self.createCalibrateButton(readerFrame, lambda num=readerNumber: self.calibrateReader(num)),
                self.createAddReaderButton(readerFrame, lambda num=readerNumber: self.createGuidedSetup(num)),
            )

    def createGuidedSetup(self, readerNumber):
        self.getReaderFrame(readerNumber).setupFrame.tkraise()
        self.getReaderFrame(readerNumber).showSetupFrame()

    def connectNewReader(self, readerNumber):
        shouldCalibrate = self.connectFn(readerNumber)
        readerFrame = self.getReaderFrame(readerNumber)
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
        self.startFn(readerNumber)
        readerFrame = self.getReaderFrame(readerNumber)
        readerFrame.startButton.disable()
        readerFrame.stopButton.enable()
        readerFrame.timer.resetTimer()

    def stopReader(self, readerNumber):
        stopReaderThread = threading.Thread(target=self.stopFn, args=(readerNumber,), daemon=True)
        stopReaderThread.start()

    def calibrateReader(self, readerNumber):
        calibrateReaderThread = threading.Thread(target=self.calibrateFn, args=(readerNumber,), daemon=True)
        calibrateReaderThread.start()

    def getIndicator(self, readerNumber):
        return self.getReaderFrame(readerNumber).indicatorCanvas, self.getReaderFrame(readerNumber).indicator

    def getPlottingFrame(self, readerNumber):
        return self.getReaderFrame(readerNumber).plotFrame

    def getReaderFrame(self, readerNumber) -> ReaderFrame:
        return self.readerFrames[readerNumber]

    def getTimer(self, readerNumber) -> RunningTimer:
        return self.getReaderFrame(readerNumber).timer

    def createPlotFrame(self, readerFrame):
        plottingFrame = tk.Frame(readerFrame, bg=self.Colors.secondaryColor, bd=5)
        plottingFrame.grid(row=1, column=0, columnspan=3)
        plottingFrame.grid_remove()
        return plottingFrame

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
    def createHeader(readerFrame, readerNumber):
        header = tk.Label(readerFrame, text=f"Vessel {readerNumber}", font=FontTheme().header3, background=Colors().secondaryColor, foreground=Colors().primaryColor)
        header.grid(row=0, column=1, sticky='n')
        return header

    @staticmethod
    def createConnectButton(readerFrame, invokeFn):
        connectReadersButton = ConnectReaderButton(readerFrame, invokeFn)
        connectReadersButton.button.grid(row=1, column=0, columnspan=3)
        connectReadersButton.hide()
        return connectReadersButton

    @staticmethod
    def createCalibrateButton(readerFrame, invokeFn):
        calibrateReadersButton = CalibrateReaderButton(readerFrame, invokeFn)
        calibrateReadersButton.button.grid(row=1, column=0, columnspan=3)
        calibrateReadersButton.hide()
        return calibrateReadersButton

    @staticmethod
    def createStartButton(readerFrame, invokeFn):
        startButton = StartButton(readerFrame, invokeFn)
        startButton.button.grid(row=2, column=0, sticky='sw')
        startButton.disable()
        return startButton

    @staticmethod
    def createStopButton(readerFrame, invokeFn):
        stopButton = StopButton(readerFrame, invokeFn)
        stopButton.button.grid(row=2, column=2, sticky='se')
        stopButton.disable()
        return stopButton
