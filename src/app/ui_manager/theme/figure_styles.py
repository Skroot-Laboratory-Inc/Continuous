import matplotlib.pyplot as plt

from src.app.ui_manager.theme import Colors


class FigureStyles:
    def __init__(self):
        self.applyGridLines = True
        self.axis = "both"
        self.which = "major"
        self.line_style = "-"
        self.alpha = 0.3
        self.z_order = 0
        self.y_soft_max = 6
        self.x_soft_max = 8

    @staticmethod
    def applyGenericStyles():
        rc = {
            "figure.figsize": (3, 2.5),
            "axes.spines.top": True,
            "axes.spines.right": True,
            "axes.edgecolor": Colors().plot.axes,
            "axes.facecolor": Colors().plot.background,
            "axes.linewidth": 1.0,
            "axes.axisbelow": True,
            "axes.grid": False,
            "font.family": "DejaVu Sans",
            "savefig.bbox": "tight",
            "axes.titlecolor": Colors().plot.axes,
            "figure.facecolor": Colors().plot.background,
            "grid.color": Colors().plot.gridlines,
            "ytick.color": Colors().plot.axes,
            "xtick.color": Colors().plot.axes,
            "axes.labelcolor": Colors().plot.axes
        }
        plt.rcParams['savefig.facecolor'] = '#232323'  # Background around the plot (figure area)
        plt.rcParams.update(rc)
