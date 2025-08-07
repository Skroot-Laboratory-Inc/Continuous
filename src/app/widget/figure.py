from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.widgets import Button
from reactivex.subject import BehaviorSubject
import tkinter as tk
import warnings

from src.app.ui_manager.theme.figure_styles import FigureStyles

warnings.filterwarnings("ignore", category=UserWarning,
                       message="This figure includes Axes that are not compatible with tight_layout")

from src.app.ui_manager.theme.colors import Colors


class FigureCanvas:
    def __init__(self, yAxisLabel, xAxisLabel, backgroundColor, title, tickSize=7, labelSize=9):
        self.frequencyFigure = Figure()
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
        self.FigureStyles = FigureStyles()
        self.FigureStyles.applyGenericStyles()
        self.button_ax = None

    def createToggle(self):
        # Only create the button if it doesn't exist or if the axes was cleared
        if not hasattr(self, 'button_ax') or self.button_ax not in self.frequencyFigure.axes:
            self.button_ax = self.frequencyFigure.add_axes([0.15, 0.75, 0.2, 0.1])
            self.button_ax.set_zorder(1000)
            self.button_ax.patch.set_alpha(0.5)
            self.toggle_button = Button(self.button_ax, 'Toggle', color=Colors().primaryColor,
                                        hovercolor=Colors().primaryColor)
            self.toggle_button.on_clicked(self.toggle_view)
            self.toggle_button.label.set_color(Colors().secondaryColor)
        return self.toggle_button

    def toggle_view(self, event):
        self.showSgi.on_next(not self.showSgi.value)

    def redrawPlot(self):
        self.frequencyFigure.clear()
        if self.reachedEquilibration:
            self.toggle_button = self.createToggle()
        self.currentPlot = self.frequencyFigure.add_subplot(111)
        self.currentPlot.grid(
            self.FigureStyles.applyGridLines,
            axis=self.FigureStyles.axis,
            which=self.FigureStyles.which,
            linestyle=self.FigureStyles.line_style,
            color=self.FigureStyles.color,
            alpha=self.FigureStyles.alpha,
            zorder=self.FigureStyles.z_order,
        )
        self.currentPlot.set_ylabel(self.yAxisLabel, color=Colors().lightPrimaryColor, fontsize=self.labelSize)
        self.currentPlot.set_title(self.title, fontsize=self.labelSize)
        self.currentPlot.set_xlabel(self.xAxisLabel, fontsize=self.labelSize)
        self.currentPlot.tick_params(axis='both', which='minor', labelsize=self.labelSize)
        self.currentPlot.tick_params(axis='both', which='major', labelsize=self.labelSize)
        self.currentPlot.xaxis.set_major_locator(MaxNLocator(nbins=6, prune=None, integer=True))
        self.currentPlot.yaxis.set_major_locator(MaxNLocator(nbins=6, prune=None, integer=True))

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

    def setYAxisLimits(self, bottom=0, top=6):
        self.currentPlot.set_ylim(bottom=bottom, top=top)

    def setXAxisLimits(self, left=0, right=8):
        self.currentPlot.set_xlim(left=left, right=right)

    def setTitle(self, title):
        self.title = title

