import tkinter as tk

from src.app.widget.timer import RunningTimer


class ReaderFrame:
    def __init__(self, frame: tk.Frame, createButton: tk.Button, plotFrame: tk.Frame, timer: RunningTimer, indicator, startButton: tk.Button, stopButton: tk.Button):
        self.frame = frame
        self.createButton = createButton
        self.plotFrame = plotFrame
        self.timer = timer
        self.indicator = indicator
        self.startButton = startButton
        self.stopButton = stopButton

