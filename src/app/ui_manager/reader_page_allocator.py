import tkinter as tk

from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors


class ReaderPageAllocator:
    def __init__(self, readerPage: tk.Frame, readersOnScreen):
        self.readerPage = readerPage
        self.maxReadersPerScreen = GuiProperties().maxReadersPerScreen
        self.readersOnScreen = readersOnScreen
        self.Colors = Colors()
        self.readerFrames = {}
        self.positions = {
            0: {"row": 0, "column": 0},
            1: {"row": 0, "column": 1},
            2: {"row": 1, "column": 0},
            3: {"row": 1, "column": 1}
        }
        self.createReaderFrames()

    def createReaderFrames(self):
        for readerNumber in range(1, self.readersOnScreen+1):
            readerFrame = tk.Frame(self.readerPage, bg=self.Colors.secondaryColor, bd=5)
            readerFrame.grid_columnconfigure(0, weight=2, minsize=35)
            readerFrame.grid_columnconfigure(1, weight=1, minsize=35)
            readerFrame.grid_rowconfigure(0, weight=1, minsize=400)
            if self.readersOnScreen != 1:
                position = (readerNumber-1) % self.maxReadersPerScreen
                readerFrame.grid(
                    row=self.positions[position]["row"],
                    column=self.positions[position]["column"],
                    sticky='ew')
            else:
                readerFrame.grid(row=0, column=0, columnspan=2, rowspan=2, sticky='ew')
            self.readerFrames[readerNumber] = readerFrame

    def getReaderFrame(self, readerNumber):
        position = (readerNumber - 1) % self.maxReadersPerScreen + 1
        if readerNumber % self.maxReadersPerScreen != 0:
            return self.readerFrames[position]
        else:
            return self.readerFrames[position]

    def createIndicator(self, readerNumber, defaultIndicatorColor):
        if self.readersOnScreen > 1:
            indicatorCanvas = tk.Canvas(
                self.getReaderFrame(readerNumber),
                height=34,
                width=34,
                bg="white",
                highlightbackground="white",
                bd=0)
            indicator = indicatorCanvas.create_circle(
                x=17, y=17, r=15, fill=defaultIndicatorColor, outline="black", width=2)
        else:
            indicatorCanvas = tk.Canvas(
                self.getReaderFrame(readerNumber),
                height=54,
                width=54,
                bg="white",
                highlightbackground="white",
                bd=0)
            indicator = indicatorCanvas.create_circle(
                x=27, y=27, r=25, fill=defaultIndicatorColor, outline="black", width=2)
        indicatorCanvas.grid(row=0, column=1)
        return indicatorCanvas, indicator

    def createPlotFrame(self, readerNumber):
        plottingFrame = tk.Frame(self.getReaderFrame(readerNumber), bg=self.Colors.secondaryColor, bd=5)
        plottingFrame.grid(row=0, column=0)
        return plottingFrame
