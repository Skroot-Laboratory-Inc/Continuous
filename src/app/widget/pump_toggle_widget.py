import tkinter as tk

from src.app.use_case.flow_cell.pump.pump_manager import PumpManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.sliding_toggle import ToggleSwitch


class PumpToggleWidget:
    """
    A UI widget that displays a pump toggle switch with status label.
    Uses PumpManager for pump control - does not manage subscriptions itself.
    """

    def __init__(self, parent_widget: tk.Widget, pump_manager: PumpManager):
        """
        Initialize the PumpToggleWidget.

        Args:
            parent_widget: The tkinter parent widget
            pump_manager: The PumpManager instance for pump control
        """
        self.parent_widget = parent_widget
        self.pump_manager = pump_manager

        self.control_frame = tk.Frame(parent_widget, bg=Colors().body.background)
        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=0)

        self.statusLabel = tk.Label(
            self.control_frame,
            text="Pump OFF",
            bg=Colors().body.background,
            foreground=Colors().body.text
        )
        self.statusLabel.grid(row=0, column=1, sticky="ns")

        self.toggle_switch = ToggleSwitch(
            self.control_frame,
            self.pump_manager.getToggleSubject()
        )
        self.toggle_switch.getWidget().grid(
            row=0,
            column=0,
            sticky="e",
            ipadx=10,
            ipady=WidgetTheme().internalPadding
        )

        self._onStateChange = self._createStateChangeHandler()
        self.pump_manager.registerStateListener(self._onStateChange)

    def _createStateChangeHandler(self):
        """Create a state change handler that updates the status label."""
        def handler(state: bool):
            if state:
                self.statusLabel.config(text="Pump ON")
            else:
                self.statusLabel.config(text="Pump OFF")
        return handler

    def getWidget(self):
        """Get the control frame widget for UI placement."""
        return self.control_frame

    def cleanup(self):
        """Clean up resources - call this before destroying the widget."""
        self.pump_manager.unregisterStateListener(self._onStateChange)
        self.toggle_switch.cleanup()
