import csv
import logging
import os
import tkinter as tk
import tkinter.ttk as ttk

from analysis import Analysis
from figure import FigureCanvas
from helper_functions import frequencyToIndex
from notes import ExperimentNotes


class SecondAxis(Analysis):
    def __init__(self, readerNumber, secondAxisTitle):
        self.secondAxisValues = []
        self.secondAxisTime = []
        self.readerNumber = readerNumber
        self.secondAxisTitle = secondAxisTitle

    def addSecondAxisMenubar(self, menu):
        menu.add_command(label=f"Reader {self.readerNumber}", command=lambda: self.typeSecondAxisValues())

    def typeSecondAxisValues(self):
        if self.secondAxisTitle == "":
            self.secondAxisTitle = tk.simpledialog.askstring(
                f'Reader {self.readerNumber} second y-axis title',
                f'Enter the title for the second axis for reader {self.readerNumber} here. \n Common options include "Viability (%)" or Cell Count (cells/mL)')
            logging.info(f'second axis title for Reader {self.readerNumber} entered: {self.secondAxisTitle}')
        value = tk.simpledialog.askfloat(f'Reader {self.readerNumber} {self.secondAxisTitle}',
                                         f'Enter the value for {self.secondAxisTitle} and reader {self.readerNumber} here. \n Numbers only')
        if value is not None:
            self.secondAxisTime.append(self.time[-1])
            self.secondAxisValues.append(value)
            with open(f'{self.savePath}/secondAxis.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time (hours)', self.secondAxisTitle])
                writer.writerows(zip(self.secondAxisTime, self.secondAxisValues))
            logging.info(f'second axis value for Reader {self.readerNumber} entered: {value}')


class Plotting(SecondAxis, ExperimentNotes):
    def __init__(self, readerColor, outerFrame, readerNumber, AppModule, secondAxisTitle=""):
        SecondAxis.__init__(self, readerNumber, secondAxisTitle)
        ExperimentNotes.__init__(self, readerNumber)
        self.AppModule = AppModule
        self.frequencyPlot = None
        self.frequencyCanvas = None
        self.frequencyFrame = None
        self.readerColor = readerColor
        self.ReaderFigureCanvas = FigureCanvas(
            readerColor,
            f'Signal Check Reader {self.readerNumber}',
            'Frequency (MHz)',
            None,
            f'Signal Check Reader {self.readerNumber}',
            self.secondAxisTitle
        )
        self.plotFrequencyButton = ttk.Button(outerFrame, text="Real Time Plot", command=lambda: self.plotFrequencies())
        self.freqToggleSet = ''

    def setToggle(self, toggle):
        self.freqToggleSet = toggle
        # Changes to the UI need to be done in the UI thread, where the button was placed, otherwise weird issues occur.
        self.plotFrequencyButton.invoke()

    def plotFrequencies(self):
        if len(self.time) > 0:
            if self.freqToggleSet == "SGI":
                self.plotGrowthIndex()
            elif self.freqToggleSet == "Signal Check":
                self.plotSignal()

    def plotGrowthIndex(self):
        self.ReaderFigureCanvas.setYAxisLabel('Skroot Growth Index (SGI)')
        self.ReaderFigureCanvas.setXAxisLabel('Time (hours)')
        self.ReaderFigureCanvas.setTitle(f'SGI Reader {self.readerNumber}')
        self.ReaderFigureCanvas.redrawPlot()
        if self.AppModule.denoiseSet:
            yPlot = frequencyToIndex(self.zeroPoint, self.denoiseFrequencySmooth)
            self.ReaderFigureCanvas.scatter(self.denoiseTimeSmooth, yPlot, 20, self.readerColor)
        else:
            yPlot = frequencyToIndex(self.zeroPoint, self.minFrequencySmooth)
            self.ReaderFigureCanvas.scatter(self.time, yPlot, 20, self.readerColor)
        for xvalue in self.notesTimestamps:
            self.ReaderFigureCanvas.addVerticalLine(xvalue)
        self.ReaderFigureCanvas.addSecondAxis(self.secondAxisTime, self.secondAxisValues)
        self.ReaderFigureCanvas.drawCanvas(self.frequencyFrame)
        self.ReaderFigureCanvas.saveAs(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg')

    def plotSignal(self):
        self.ReaderFigureCanvas.setYAxisLabel('Signal Check')
        self.ReaderFigureCanvas.setXAxisLabel('Frequency (MHz)')
        self.ReaderFigureCanvas.setTitle(f'Signal Check Reader {self.readerNumber}')
        self.ReaderFigureCanvas.redrawPlot()
        self.ReaderFigureCanvas.scatter(self.scanFrequency, self.scanMagnitude, 20, 'black')
        self.ReaderFigureCanvas.scatter(self.minFrequencySmooth[-1], self.minDbSmooth[-1], 30, 'red')
        self.ReaderFigureCanvas.drawCanvas(self.frequencyFrame)
        self.ReaderFigureCanvas.saveAs(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg')

    def createFrequencyFrame(self, outerFrame, totalNumberOfReaders):
        spaceForPlots = 0.9
        self.frequencyFrame = tk.Frame(outerFrame, bg=self.AppModule.white, bd=5)
        relx, rely = 0, 0
        if totalNumberOfReaders > 1:
            if (self.readerNumber % 5) == 1:
                relx, rely = 0, 0
            elif (self.readerNumber % 5) == 2:
                relx, rely = 0.33, 0
            elif (self.readerNumber % 5) == 3:
                relx, rely = 0.67, 0
            elif (self.readerNumber % 5) == 4:
                relx, rely = 0, 0.5 * spaceForPlots
            elif (self.readerNumber % 5) == 0:
                relx, rely = 0.33, 0.5 * spaceForPlots
            else:
                pass
            if self.AppModule.cellApp:
                self.frequencyFrame.place(relx=relx, rely=rely, relwidth=0.25, relheight=0.45 * spaceForPlots)
            else:
                self.frequencyFrame.place(relx=relx, rely=rely, relwidth=0.25, relheight=0.45 * spaceForPlots)
        else:
            relx, rely = 0, 0
            if self.AppModule.cellApp:
                self.frequencyFrame.place(relx=relx, rely=rely, relwidth=0.57, relheight=0.9 * spaceForPlots)
            else:
                self.frequencyFrame.place(relx=relx, rely=rely, relwidth=0.67, relheight=0.9 * spaceForPlots)
