from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import Button
from reactivex.subject import BehaviorSubject
import tkinter as tk
import warnings
warnings.filterwarnings("ignore", category=UserWarning,
                       message="This figure includes Axes that are not compatible with tight_layout")

from src.app.theme.colors import Colors


class FigureCanvas:
    def __init__(self, yAxisLabel, xAxisLabel, backgroundColor, title, tickSize=7, labelSize=9):
        self.frequencyFigure = Figure(figsize=(3, 2.5))
        self.frequencyFigure.set_layout_engine("tight")
        self.currentPlot = None
        self.tickSize = tickSize
        self.labelSize = labelSize
        self.yAxisLabel = yAxisLabel
        self.xAxisLabel = xAxisLabel
        self.backgroundColor = backgroundColor
        self.title = title
        self.frequencyCanvas = None
        self.showSgi = BehaviorSubject(False)
        self.toggle_button = self.createToggle()
        self.reachedEquilibration = False

    def createToggle(self):
        button_ax = self.frequencyFigure.add_axes([0.79, 0.89, 0.2, 0.1])
        toggle_button = Button(button_ax, 'Toggle', color=Colors().primaryColor, hovercolor=Colors().primaryColor)
        toggle_button.on_clicked(self.toggle_view)
        toggle_button.label.set_color(Colors().secondaryColor)
        return toggle_button

    def toggle_view(self, event):
        self.showSgi.on_next(not self.showSgi.value)

    def redrawPlot(self):
        self.frequencyFigure.clear()
        if self.reachedEquilibration:
            self.toggle_button = self.createToggle()
        self.currentPlot = self.frequencyFigure.add_subplot(111)
        self.currentPlot.set_ylabel(self.yAxisLabel, color=Colors().lightPrimaryColor, fontsize=self.labelSize)
        self.currentPlot.set_title(self.title, fontsize=self.labelSize)
        self.currentPlot.set_xlabel(self.xAxisLabel, fontsize=self.labelSize)
        self.currentPlot.tick_params(axis='both', which='minor', labelsize=self.labelSize)
        self.currentPlot.tick_params(axis='both', which='major', labelsize=self.labelSize)

    def drawCanvas(self, frame):
        if self.frequencyCanvas is None:
            self.frequencyCanvas = FigureCanvasTkAgg(self.frequencyFigure, master=frame)
        self.frequencyCanvas.draw()
        self.frequencyCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
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

