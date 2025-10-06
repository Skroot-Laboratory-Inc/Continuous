import tkinter as tk

# Import the appropriate pump based on environment
import platform

from src.app.reader.pump.pump_interface import PumpInterface
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.sliding_toggle import ToggleSwitch


class PumpController:
    """
    A controller class that wraps a pump and provides UI integration with a toggle switch.
    This keeps the pump classes clean and focused on their core functionality.
    """

    def __init__(self, parent_widget, pump: PumpInterface):
        """
        Initialize the PumpController with a pump and toggle switch.

        Args:
            parent_widget: The tkinter parent widget for the toggle switch
        """
        self.parent_widget = parent_widget
        self.pump = pump

        self.control_frame = tk.Frame(parent_widget, bg="white")
        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=0)
        self.statusLabel = tk.Label(self.control_frame, text="Pump OFF", bg=Colors().secondaryColor)
        self.statusLabel.grid(row=0, column=1, sticky="ns")
        self.toggle_switch = ToggleSwitch(
            self.control_frame,
            self.pump.getToggleSubject()
        )
        self.pump.getToggleSubject().subscribe(self.onToggleChange)
        self.toggle_switch.getWidget().grid(row=0, column=0, sticky="e", ipadx=10, ipady=WidgetTheme().internalPadding)

    def getToggle(self):
        """Get the toggle switch widget for UI placement"""
        return self.control_frame

    def onToggleChange(self, state: bool):
        if state:
            self.statusLabel.config(text="Pump ON")
        else:
            self.statusLabel.config(text="Pump OFF")
            
    def getPump(self):
        """Get the underlying pump instance"""
        return self.pump

    def start(self):
        """Start the pump"""
        self.toggle_switch.set_state(True)

    def stop(self):
        """Stop the pump"""
        self.toggle_switch.set_state(False)

    def setFlowRate(self, speed: float):
        """Set pump speed"""
        return self.pump.setFlowRate(speed)

    def set_toggle_state(self, state: bool):
        """Programmatically set the toggle state"""
        self.toggle_switch.set_state(state)

    def get_toggle_state(self):
        """Get the current toggle state"""
        return self.toggle_switch.get_state()

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.pump, 'cleanup'):
            self.pump.cleanup()