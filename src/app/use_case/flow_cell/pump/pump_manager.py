import tkinter as tk
from typing import Callable, List

from src.app.properties.pump_properties import PumpProperties
from src.app.use_case.flow_cell.pump.pump_interface import PumpInterface
from src.app.widget.sidebar.configurations.pump_priming_configuration import PumpPrimingConfiguration


class PumpManager:
    """
    Centralized pump management that handles pump state, subscriptions, and motor
    RPM control. This should be created once and shared across all UI components
    that need pump control.
    """

    def __init__(self, pump: PumpInterface):
        """
        Initialize the PumpManager with a pump.

        Args:
            pump: The pump interface to control
        """
        self.pump = pump
        self.primingEnabled = True
        self.rpm = PumpProperties().defaultRpm
        self._state_listeners: List[Callable[[bool], None]] = []

        # Single subscription to the pump's toggle subject
        self._subscription = self.pump.getToggleSubject().subscribe(self._onPumpStateChange)

    def _onPumpStateChange(self, state: bool):
        """Handle pump state changes and update RPM accordingly."""
        if state:
            # Pump is turning ON - set appropriate RPM
            if self.primingEnabled:
                self.pump.setRpm(PumpPrimingConfiguration().getConfig())
            else:
                self.pump.setRpm(self.rpm)

        # Notify all registered listeners
        for listener in self._state_listeners:
            try:
                listener(state)
            except tk.TclError:
                # Widget was destroyed, will be cleaned up later
                pass

    def registerStateListener(self, listener: Callable[[bool], None]):
        """Register a callback to be notified of pump state changes."""
        self._state_listeners.append(listener)
        # Immediately notify with current state
        current_state = self.pump.getToggleSubject().value
        try:
            listener(current_state)
        except tk.TclError:
            pass

    def unregisterStateListener(self, listener: Callable[[bool], None]):
        """Unregister a state change listener."""
        if listener in self._state_listeners:
            self._state_listeners.remove(listener)

    def setPriming(self, enabled: bool):
        """Enable or disable priming mode."""
        self.primingEnabled = enabled

    def setRpm(self, rpm: float):
        """Set the normal (non-priming) motor RPM."""
        self.rpm = rpm
        if self.isRunning() and not self.primingEnabled:
            self.pump.setRpm(rpm)

    def getMinRpm(self) -> float:
        """Minimum selectable motor RPM."""
        return PumpProperties().defaultRpm

    def getMaxRpm(self) -> float:
        """Maximum selectable motor RPM."""
        return PumpProperties().primingRpm

    def start(self):
        """Turn the pump ON."""
        self.pump.getToggleSubject().on_next(True)

    def stop(self):
        """Turn the pump OFF."""
        self.pump.getToggleSubject().on_next(False)

    def getToggleSubject(self):
        """Get the pump's toggle subject for UI binding."""
        return self.pump.getToggleSubject()

    def isRunning(self) -> bool:
        """Check if the pump is currently running."""
        return self.pump.getToggleSubject().value

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, '_subscription') and self._subscription:
            self._subscription.dispose()
            self._subscription = None
        self._state_listeners.clear()
