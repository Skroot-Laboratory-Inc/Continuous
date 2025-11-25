from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.widgets import Button
from reactivex.subject import BehaviorSubject
import tkinter as tk
import warnings
import time

from src.app.ui_manager.theme.figure_styles import FigureStyles
from src.app.widget.sidebar.configurations.secondary_axis_type import SecondaryAxisType
from src.app.widget.sidebar.configurations.secondary_axis_units import SecondaryAxisUnits

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
        self.last_toggle_time = 0
        self.toggle_debounce_ms = 300  # Minimum time between clicks in milliseconds

    def createToggle(self):
        """Create or recreate the toggle button with proper cleanup."""
        # Clean up existing button if it exists
        if hasattr(self, 'toggle_button') and self.toggle_button is not None:
            try:
                # Disconnect any existing event handlers
                self.toggle_button.disconnect_events()
            except (AttributeError, RuntimeError):
                pass  # Button may not have disconnect method or already disconnected

        # Only create the button if it doesn't exist or if the axes was cleared
        if not hasattr(self, 'button_ax') or self.button_ax not in self.frequencyFigure.axes:
            self.button_ax = self.frequencyFigure.add_axes([0.15, 0.75, 0.2, 0.1])
            self.button_ax.set_zorder(1000)
            self.button_ax.patch.set_alpha(0.5)
            self.toggle_button = Button(self.button_ax, 'Toggle', color=Colors().buttons.background,
                                        hovercolor=Colors().buttons.background)
            self.toggle_button.on_clicked(self.toggle_view)
            self.toggle_button.label.set_color(Colors().body.background)
        return self.toggle_button

    def toggle_view(self, event):
        """Toggle view with debouncing and error handling for mouse grab issues."""
        current_time = time.time() * 1000  # Convert to milliseconds

        # Debounce: Ignore clicks that are too close together
        if current_time - self.last_toggle_time < self.toggle_debounce_ms:
            return

        self.last_toggle_time = current_time

        try:
            # Release any existing mouse grab before processing
            if hasattr(event.canvas, 'release_mouse'):
                try:
                    event.canvas.release_mouse(self.button_ax)
                except (RuntimeError, AttributeError):
                    pass  # No grab to release or already released

            self.showSgi.on_next(not self.showSgi.value)

        except RuntimeError as e:
            # Handle the "Another Axes already grabs mouse input" error
            if "grabs mouse input" in str(e):
                # Try to force release and retry once
                try:
                    # Force release by accessing the internal state
                    event.canvas._button = None
                    self.showSgi.on_next(not self.showSgi.value)
                except Exception:
                    # If still failing, just update the state without the event handling
                    self.showSgi.on_next(not self.showSgi.value)
            else:
                raise  # Re-raise unexpected errors

    def addSecondAxis(self, times, values):
        if values:
            ax2 = self.currentPlot.twinx()
            ax2.scatter(times, values, s=20, color='k')
            ax2.set_ylabel(f"{SecondaryAxisType().getConfig()} {SecondaryAxisUnits().getAsUnit()}", color='k')
        self.frequencyFigure.tight_layout()

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
        self.currentPlot.set_ylabel(self.yAxisLabel, fontsize=self.labelSize)
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

