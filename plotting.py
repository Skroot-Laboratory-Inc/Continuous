import csv
import os
import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure

import logger


class SecondAxis:
    def addSecondAxisMenubar(self, menu):
        menu.add_command(label=f"Reader {self.readerNumber}", command=lambda: self.typeSecondAxisValues())

    def typeSecondAxisValues(self):
        if self.secondAxisTitle == None:
            self.secondAxisTitle = tk.simpledialog.askstring(f'Reader {self.readerNumber} second y-axis title',
                                                             f'Enter the title for the second axis for reader {self.readerNumber} here. \n Common options include "Viability (%)" or Cell Count (cells/mL)')
            logger.info(f'second axis title for Reader {self.readerNumber} entered: {self.secondAxisTitle}')
        value = tk.simpledialog.askfloat(f'Reader {self.readerNumber} {self.secondAxisTitle}',
                                         f'Enter the value for {self.secondAxisTitle} and reader {self.readerNumber} here. \n Numbers only')
        if value != None:
            self.secondAxisTime.append(self.time[-1])
            self.secondAxisValues.append(value)
            with open(f'{self.savePath}/secondAxis.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time (hours)', self.secondAxisTitle])
                writer.writerows(zip(self.secondAxisTime, self.secondAxisValues))
            logger.info(f'second axis value for Reader {self.readerNumber} entered: {value}')


class Plotting:
    def plotFrequencies(self):
        if self.AppModule.freqToggleSet == "Frequency":
            self.plotFrequency()
        elif self.AppModule.freqToggleSet == "Signal Strength":
            self.plotMagnitude()
        elif self.AppModule.freqToggleSet == "Signal Check":
            self.plotSignal()

    def plotMagnitude(self):
        try:
            self.frequencyFigure.clear()
        except:
            self.frequencyFigure = Figure(figsize=(3, 3))
            self.frequencyFigure.set_tight_layout(True)
        self.frequencyPlot = self.frequencyFigure.add_subplot(111)
        self.frequencyPlot.set_ylabel('Signal Strength (dB)', color='#1f77b4')
        self.frequencyPlot.set_title(f'Signal Strength Reader {self.readerNumber}')
        if self.AppModule.denoiseSet:
            self.frequencyPlot.scatter(self.denoiseTimeDbSmooth, self.denoiseTotalMinSmooth, s=20,
                                       color=self.readerColor)
        else:
            self.frequencyPlot.scatter(self.time, self.minDbSmooth, s=20, color=self.readerColor)
        for xvalue in self.notesTimestamps:
            self.addVerticalLine(self.frequencyPlot, xvalue)
        self.addSecondAxis(self.frequencyPlot)
        self.frequencyPlot.set_xlabel('Time (hours)')
        self.frequencyPlot.set_facecolor(self.backgroundColor)
        self.frequencyFigure.savefig(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg')
        if self.frequencyCanvas is None:
            self.frequencyCanvas = FigureCanvasTkAgg(self.frequencyFigure, master=self.frequencyFrame)
        self.frequencyCanvas.draw()
        self.frequencyCanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plotFrequency(self):
        try:
            self.frequencyFigure.clear()
        except:
            self.frequencyFigure = Figure(figsize=(3, 3))
            self.frequencyFigure.set_tight_layout(True)
        self.frequencyPlot = self.frequencyFigure.add_subplot(111)
        self.frequencyPlot.set_ylabel('Frequency (MHz)', color=self.readerColor)
        self.frequencyPlot.set_title(f'Resonant Frequency Reader {self.readerNumber}')
        if self.AppModule.denoiseSet:
            self.frequencyPlot.scatter(self.denoiseTimeSmooth, self.denoiseFrequencySmooth, s=20,
                                       color=self.readerColor)
        else:
            self.frequencyPlot.scatter(self.time, self.minFrequencySmooth, s=20, color=self.readerColor)
        for xvalue in self.notesTimestamps:
            self.addVerticalLine(self.frequencyPlot, xvalue)
        self.addSecondAxis(self.frequencyPlot)
        if self.waterShift is not None:
            self.frequencyPlot.set_ylim([self.waterFreq - 2, self.airFreq + 2])
        self.frequencyPlot.set_xlabel('Time (hours)')
        self.frequencyPlot.set_facecolor(self.backgroundColor)
        self.frequencyFigure.savefig(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg')
        if self.frequencyCanvas is None:
            self.frequencyCanvas = FigureCanvasTkAgg(self.frequencyFigure, master=self.frequencyFrame)
        self.frequencyCanvas.draw()
        self.frequencyCanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def addVerticalLine(self, plot, x):
        plot.axvline(x=x)

    def plotSignal(self):
        try:
            self.frequencyFigure.clear()
        except:
            self.frequencyFigure = Figure(figsize=(3, 3))
            self.frequencyFigure.set_tight_layout(True)
        self.frequencyPlot = self.frequencyFigure.add_subplot(111)
        self.frequencyPlot.set_title(f'Signal Check Reader {self.readerNumber}')
        self.frequencyPlot.scatter(self.scanFrequency, self.scanMagnitude, s=20, color='black')
        self.frequencyPlot.scatter(self.minFrequencySmooth[-1], self.minDbSmooth[-1], s=30, color='red')
        self.frequencyPlot.set_xlabel('Frequency (MHz)')
        self.frequencyFigure.savefig(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg')
        if self.frequencyCanvas is None:
            self.frequencyCanvas = FigureCanvasTkAgg(self.frequencyFigure, master=self.frequencyFrame)
        self.frequencyCanvas.draw()
        self.frequencyCanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def addSecondAxis(self, plot):
        if self.secondAxisTitle is not None:
            ax2 = plot.twinx()
            ax2.scatter(self.secondAxisTime, self.secondAxisValues, s=20, color='k')
            ax2.set_ylabel(self.secondAxisTitle, color='k')

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
                relx, rely = 0, 0.5*spaceForPlots
            elif (self.readerNumber % 5) == 0:
                relx, rely = 0.33, 0.5*spaceForPlots
            else:
                pass
            if self.AppModule.cellApp:
                self.frequencyFrame.place(relx=relx, rely=rely, relwidth=0.27, relheight=0.45*spaceForPlots)
            else:
                self.frequencyFrame.place(relx=relx, rely=rely, relwidth=0.27, relheight=0.45*spaceForPlots)
        else:
            relx, rely = 0, 0
            if self.AppModule.cellApp:
                self.frequencyFrame.place(relx=relx, rely=rely, relwidth=0.57, relheight=0.9*spaceForPlots)
            else:
                self.frequencyFrame.place(relx=relx, rely=rely, relwidth=0.67, relheight=0.9*spaceForPlots)

    def createUpdateFrequenciesButton(self, outerFrame):
        self.plotFrequencyButton = ttk.Button(outerFrame, text="Real Time Plot", command=lambda: self.plotFrequencies())
