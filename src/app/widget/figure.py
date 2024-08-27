import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class FigureCanvas:
    def __init__(self, readerColor, yAxisLabel, xAxisLabel, backgroundColor, title, secondAxisTitle, tickSize=9, labelSize=11):
        self.frequencyFigure = Figure()
        self.frequencyFigure.set_layout_engine("tight")
        self.currentPlot = None
        self.tickSize = tickSize
        self.labelSize = labelSize
        self.readerColor = readerColor
        self.yAxisLabel = yAxisLabel
        self.xAxisLabel = xAxisLabel
        self.secondAxisTitle = secondAxisTitle
        self.backgroundColor = backgroundColor
        self.title = title
        self.frequencyCanvas = None

    def redrawPlot(self):
        self.frequencyFigure.clear()
        self.currentPlot = self.frequencyFigure.add_subplot(111)
        self.currentPlot.set_ylabel(self.yAxisLabel, color=self.readerColor, fontsize=self.labelSize)
        self.currentPlot.set_title(self.title, fontsize=self.labelSize)
        self.currentPlot.set_xlabel(self.xAxisLabel, fontsize=self.labelSize)
        self.currentPlot.tick_params(axis='both', which='minor', labelsize=self.labelSize)
        self.currentPlot.tick_params(axis='both', which='major', labelsize=self.labelSize)
        # TODO Update this to work with contamination algorithm
        # self.currentPlot.set_facecolor(self.backgroundColor)

    def drawCanvas(self, frame):
        if self.frequencyCanvas is None:
            self.frequencyCanvas = FigureCanvasTkAgg(self.frequencyFigure, master=frame)
        self.frequencyCanvas.draw()
        self.frequencyCanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def scatter(self, x, y, size, color):
        self.currentPlot.scatter(x, y, size, color=color)

    def addSecondAxis(self, x, values):
        if values:
            ax2 = self.currentPlot.twinx()
            ax2.scatter(x, values, s=20, color='k')
            ax2.set_ylabel(self.secondAxisTitle, color='k')

    def saveAs(self, filename):
        self.frequencyFigure.savefig(filename, dpi=500)

    def addVerticalLine(self, x):
        self.currentPlot.axvline(x=x)

    def setBackgroundColor(self, color):
        self.backgroundColor = color

    def setYAxisLabel(self, label):
        self.yAxisLabel = label

    def setXAxisLabel(self, label):
        self.xAxisLabel = label

    def setTitle(self, title):
        self.title = title

