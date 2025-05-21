import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.widgets import Button


class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plot with Overlay Button")

        # State tracking
        self.show_signal = True

        # Create matplotlib figure and canvas
        self.fig = Figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a button directly on the plot
        # Position is in figure coordinates (0,0 is bottom left, 1,1 is top right)
        button_ax = self.fig.add_axes([0.81, 0.01, 0.18, 0.05])  # [left, bottom, width, height]
        self.toggle_button = Button(button_ax, 'Switch View')
        self.toggle_button.on_clicked(self.toggle_view)

        # Initial plot
        self.update_plot()

    def toggle_view(self, event):
        # Toggle the state
        self.show_signal = not self.show_signal
        self.update_plot()

    def update_plot(self):
        # Clear the current plot
        self.ax.clear()

        # Create sample data
        x = np.linspace(0, 10, 100)

        if self.show_signal:
            # Show signal data
            y = np.sin(x)
            self.ax.plot(x, y, 'b-')
            self.ax.set_title("Signal Data")
        else:
            # Show results data
            y = x ** 2 / 10
            self.ax.plot(x, y, 'r-')
            self.ax.set_title("Results Data")

        # Redraw the canvas
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.geometry("600x500")
    root.mainloop()