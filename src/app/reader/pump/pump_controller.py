import tkinter as tk

# Import the appropriate pump based on environment
import platform

from src.app.properties.pump_properties import PumpProperties
from src.app.reader.pump.pump_interface import PumpInterface
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.sidebar.configurations.pump_priming_configuration import PumpPrimingConfiguration
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
        self.primingEnabled = True
        self.speed = PumpProperties().defaultFlowRate

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
        print(self.primingEnabled, self.speed)
        if self.primingEnabled:
            self.pump.setFlowRate(PumpPrimingConfiguration().getConfig())
        else:
            self.pump.setFlowRate(self.speed)
        if state:
            self.statusLabel.config(text="Pump ON")
        else:
            self.statusLabel.config(text="Pump OFF")

    def setPriming(self, enabled: bool):
        """Enable or disable priming mode"""
        print(f"PumpController: Setting priming mode to {enabled}")
        self.primingEnabled = enabled

    def stop(self):
        """Get the underlying pump instance"""
        return self.pump.getToggleSubject().on_next(False)

    def setFlowRate(self, speed: float):
        """Set pump speed"""
        print(f"PumpController: Setting flow rate to {speed}")
        self.speed = speed

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.pump, 'cleanup'):
            self.pump.cleanup()
