from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class FigureCanvas:
    def __init__(self, readerColor, yAxisLabel, xAxisLabel, backgroundColor, title, tickSize=7, labelSize=9):
        self.frequencyFigure = Figure(figsize=(4.5, 3.5))
        self.frequencyFigure.set_layout_engine("tight")
        self.currentPlot = None
        self.tickSize = tickSize
        self.labelSize = labelSize
        self.readerColor = readerColor
        self.yAxisLabel = yAxisLabel
        self.xAxisLabel = xAxisLabel
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
        self.frequencyCanvas.get_tk_widget().pack()
        self.frequencyCanvas.get_tk_widget().update()
        self.frequencyCanvas.get_tk_widget().update_idletasks()

    def scatter(self, x, y, size, color):
        self.currentPlot.scatter(x, y, size, color=color)

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

