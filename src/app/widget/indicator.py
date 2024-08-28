import tkinter as tk

from src.app.theme.colors import Colors
from src.app.ui_manager.reader_page_allocator import ReaderPageAllocator


class Indicator:
    def __init__(self, readerNumber, readerPageAllocator: ReaderPageAllocator):
        self.Colors = Colors()
        self.indicatorColor = self.Colors.green
        self.ReaderPageAllocator = readerPageAllocator
        self.readerNumber = readerNumber
        self.indicatorCanvas, self.indicator = self.ReaderPageAllocator.createIndicator(
            self.readerNumber,
            self.indicatorColor)

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
