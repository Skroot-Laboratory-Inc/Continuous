import tkinter as tk
from tkinter import ttk

from reactivex import operators as ops, Subject

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme


class TimedProgressBar:
    def __init__(self, parent):
        """
        Create a timed progress bar.

        Args:
            parent: The parent tkinter widget/frame
        """
        self.parent = parent
        self.duration_ms = 0
        self.update_interval = 50  # Update every 50ms for smooth animation
        self.current_time = 0
        self.is_running = False
        self.completion_callback = None

        # Create a container frame for centering
        self.container_frame = tk.Frame(parent, background=Colors().body.background)
        self.container_frame.pack(expand=True)

        # Create the progress bar inside the container
        self.progress = ttk.Progressbar(
            self.container_frame,
            length=600,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress['maximum'] = 100
        self.progress.pack(ipady=WidgetTheme().internalPadding)

        # Create percentage label inside the container
        self.percent_label = tk.Label(self.container_frame, text="0%", font=FontTheme().primary, background=Colors().body.background, foreground=Colors().body.text)
        self.percent_label.pack()

    def start(self, duration_seconds, stillScanning: Subject, callback=None):
        """
        Start the progress bar.

        Args:
            duration_seconds: Duration in seconds (float or int)
            stillScanning: Subject indicating if the device is scanning. The progress bar will not stop until this is False.
            callback: Optional function to call when progress completes
        """
        if not self.is_running:
            stillScanning.pipe(
                ops.filter(lambda scanning: not scanning),
                ops.take(1)
            ).subscribe(lambda _: self.finishScanning())
            self.duration_ms = int(duration_seconds * 1000)
            self.completion_callback = callback
            self.current_time = 0
            self.progress['value'] = 0
            self.percent_label.config(text="0%")
            self.is_running = True
            self._update()

    def stop(self):
        """Stop the progress bar."""
        self.is_running = False

    def reset(self):
        """Reset the progress bar to the beginning."""
        self.is_running = False
        self.current_time = 0
        self.progress['value'] = 0
        self.percent_label.config(text="0%")

    def _update(self):
        """Internal method to update progress."""
        if self.is_running:
            self.current_time += self.update_interval

            # Calculate percentage
            percentage = min((self.current_time / self.duration_ms) * 100, 99)
            self.progress['value'] = percentage

            # Update percentage label
            self.percent_label.config(text=f"{round(percentage)}%")

            # Schedule next update
            self.parent.after(self.update_interval, self._update)

    def finishScanning(self):
        self.reset()

        # Call completion callback if provided
        if self.completion_callback:
            self.completion_callback()
