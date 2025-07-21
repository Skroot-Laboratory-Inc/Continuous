import matplotlib.pyplot as plt


class FigureStyles:
    def __init__(self):
        self.applyGridLines = True
        self.axis = "both"
        self.which = "major"
        self.line_style = "-"
        self.color = "lightgray"
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
            "axes.edgecolor": "black",
            "axes.linewidth": 1.0,
            "axes.axisbelow": True,
            "axes.grid": False,
            "font.family": "DejaVu Sans",
            "savefig.bbox": "tight",
        }
        plt.rcParams.update(rc)