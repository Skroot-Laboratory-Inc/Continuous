import tkinter as tk

from src.app.buttons.calibrate_readers import CalibrateReaderButton
from src.app.buttons.connect_reader import ConnectReaderButton
from src.app.buttons.plus_icon_button import PlusIconButton
from src.app.buttons.start_button import StartButton
from src.app.buttons.stop_button import StopButton
from src.app.widget.timer import RunningTimer


class ReaderFrame:
    def __init__(self,
                 frame: tk.Frame,
                 plotFrame: tk.Frame,
                 timer: RunningTimer,
                 indicator,
                 indicatorCanvas: tk.Canvas,
                 startButton: StartButton,
                 stopButton: StopButton,
                 # connectButton: ConnectReaderButton,
                 calibrateButton: CalibrateReaderButton,
                 createButton: PlusIconButton):
        self.frame = frame
        self.createButton = createButton
        self.plotFrame = plotFrame
        # self.connectButton = connectButton
        self.calibrateButton = calibrateButton
        self.indicatorCanvas = indicatorCanvas
        self.timer = timer
        self.indicator = indicator
        self.startButton = startButton
        self.stopButton = stopButton

    def hidePlotFrame(self):
        self.plotFrame.grid_remove()

    def showPlotFrame(self):
        self.plotFrame.grid()

