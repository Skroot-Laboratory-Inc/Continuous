import tkinter as tk

from src.app.theme.colors import Colors


class Indicator:
    def __init__(self, totalNumberOfReaders, readerNumber):
        self.Colors = Colors()
        self.indicatorColor = self.Colors.green
        self.totalNumberOfReaders = totalNumberOfReaders
        self.readerNumber = readerNumber

    def createIndicator(self, outerFrame):
        # TODO Rework this to not be so complicated, or know about the UI
        if self.totalNumberOfReaders > 1:
            self.indicatorCanvas = tk.Canvas(outerFrame, height=90, width=90, bg="white", highlightbackground="white",
                                             bd=0)
            self.indicator = self.indicatorCanvas.create_circle(17, 17, 15, fill=self.indicatorColor, outline="black",
                                                                width=2)  # x, y, r, kwds
            if (self.readerNumber % 5) == 1:
                self.indicatorCanvas.place(anchor='e', relx=0.33, rely=0.15)
            if (self.readerNumber % 5) == 2:
                self.indicatorCanvas.place(anchor='e', relx=0.66, rely=0.15)
            if (self.readerNumber % 5) == 3:
                self.indicatorCanvas.place(anchor='e', relx=1, rely=0.15)
            if (self.readerNumber % 5) == 4:
                self.indicatorCanvas.place(anchor='e', relx=0.33, rely=0.6)
            if (self.readerNumber % 5) == 0:
                self.indicatorCanvas.place(anchor='e', relx=0.66, rely=0.6)
        else:
            self.indicatorCanvas = tk.Canvas(outerFrame, height=120, width=120, bg="white", highlightbackground="white",
                                             bd=0)
            self.indicator = self.indicatorCanvas.create_circle(27, 27, 25, fill=self.indicatorColor, outline="black",
                                                                width=2)  # x, y, r, kwds
            self.indicatorCanvas.place(anchor='e', relx=0.67, rely=0.2)

    def changeIndicatorGreen(self):
        self.indicatorCanvas.itemconfig(self.indicator, fill=self.Colors.green)
        self.updateHarvestJson(self.Colors.green)

    def changeIndicatorYellow(self):
        self.indicatorCanvas.itemconfig(self.indicator, fill=self.Colors.yellow)
        self.updateHarvestJson(self.Colors.yellow)

    def changeIndicatorRed(self):
        self.indicatorCanvas.itemconfig(self.indicator, fill=self.Colors.lightRed)
        self.updateHarvestJson(self.Colors.lightRed)

    def updateHarvestJson(self, harvestColor):
        self.indicatorColor = harvestColor
