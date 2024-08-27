import math
import tkinter as tk

from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors


class ReaderPageAllocator:
    def __init__(self, readerPage: tk.Frame, readersOnScreen):
        self.readerPage = readerPage
        self.maxReadersPerScreen = GuiProperties().maxReadersPerScreen
        self.readersOnScreen = readersOnScreen
        self.Colors = Colors()
        self.readerPage.grid_rowconfigure(0, weight=1)
        self.readerPage.grid_rowconfigure(1, weight=1)
        self.readerPage.grid_columnconfigure(0, weight=1)
        self.readerPage.grid_columnconfigure(1, weight=1)
        self.readerFrames = {}
        self.positions = {
            0: {"row": 0, "column": 0},
            1: {"row": 0, "column": 1},
            2: {"row": 1, "column": 0},
            3: {"row": 1, "column": 1}
        }
        self.createReaderFrames()

    def createReaderFrames(self):
        readerFrame = tk.Frame(self.readerPage, bg=self.Colors.secondaryColor, bd=5)
        readerFrame.grid(row=0, column=0, sticky='nsew')
        readerFrame.grid_columnconfigure(0, weight=9)
        readerFrame.grid_columnconfigure(1, weight=1)
        for readerNumber in range(1, self.readersOnScreen+1):
            if self.readersOnScreen != 1:
                position = (readerNumber-1) % self.maxReadersPerScreen
                readerFrame.grid(
                    row=self.positions[position]["row"],
                    column=self.positions[position]["column"],
                    sticky='nesw')
            else:
                self.readerPage.grid_forget()
                self.readerPage.grid_rowconfigure(0, weight=1)
                self.readerPage.grid_columnconfigure(0, weight=1)
                readerFrame.grid(row=0, column=0, sticky='nesw')
            self.readerFrames[readerNumber] = readerFrame

    def getReaderFrame(self, readerNumber):
        return self.readerFrames[readerNumber]

    def createIndicator(self, readerNumber, defaultIndicatorColor):
        if self.readersOnScreen > 1:
            indicatorCanvas = tk.Canvas(
                self.getReaderFrame(readerNumber),
                height=90,
                width=90,
                bg="white",
                highlightbackground="white",
                bd=0)
            indicator = indicatorCanvas.create_circle(
                x=17, y=17, r=15, fill=defaultIndicatorColor, outline="black", width=2)
        else:
            indicatorCanvas = tk.Canvas(
                self.getReaderFrame(readerNumber),
                height=120,
                width=120,
                bg="white",
                highlightbackground="white",
                bd=0)
            indicator = indicatorCanvas.create_circle(
                x=27, y=27, r=25, fill=defaultIndicatorColor, outline="black", width=2)
        indicatorCanvas.grid(row=0, column=1, sticky='n')
        return indicatorCanvas, indicator

    def createPlotFrame(self, readerNumber):
        plottingFrame = tk.Frame(self.getReaderFrame(readerNumber), bg=self.Colors.secondaryColor, bd=5)
        plottingFrame.grid(row=0, column=0)
        return plottingFrame
