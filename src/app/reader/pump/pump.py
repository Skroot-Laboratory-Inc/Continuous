import threading
import time

import gpiod
from reactivex.subject import BehaviorSubject

from src.app.properties.pump_properties import PumpProperties
from src.app.reader.pump.pump_helpers import flowRateToStepPeriod
from src.app.reader.pump.pump_interface import PumpInterface


class Pump(PumpInterface):
    """
    A simple class to control a stepper motor pump with on/off and speed control.
    """

    def __init__(self, step_pin: int = 21, dir_pin: int = 20, enable_pin: int = 16,
                 chip_name: str = 'gpiochip0', direction: int = 1):
        """
        Initialize the stepper motor pump controller.

        Args:
            step_pin: GPIO pin for step control
            dir_pin: GPIO pin for direction control
            enable_pin: GPIO pin for enable control (active low)
            chip_name: GPIO chip name (usually 'gpiochip0' for Raspberry Pi)
            direction: Pump direction (1 for forward, 0 for reverse)
        """
        self.isRunning = False
        self.stepPeriod = flowRateToStepPeriod(PumpProperties().defaultFlowRate)
        self._stop_event = threading.Event()
        self._pump_thread = None
        self.toggleSubject = BehaviorSubject(False)  # Start with pump off
        self.toggleSubject.subscribe(self._on_toggle_changed)

        # GPIO setup
        self.chip = gpiod.Chip(chip_name)
        self.step_line = self.chip.get_line(step_pin)
        self.dir_line = self.chip.get_line(dir_pin)
        self.en_line = self.chip.get_line(enable_pin)

        # Configure as outputs
        self.step_line.request(consumer="stepper_pump", type=gpiod.LINE_REQ_DIR_OUT)
        self.dir_line.request(consumer="stepper_pump", type=gpiod.LINE_REQ_DIR_OUT)
        self.en_line.request(consumer="stepper_pump", type=gpiod.LINE_REQ_DIR_OUT)

        # Initialize pins
        self.step_line.set_value(0)
        self.dir_line.set_value(direction)
        self.en_line.set_value(1)  # Disabled initially (active low)

    def start(self):
        if self.isRunning:
            return

        self.isRunning = True
        self._stop_event.clear()

        self.en_line.set_value(0)  # Active low

        self._pump_thread = threading.Thread(target=self._pump_continuously, daemon=True)
        self._pump_thread.start()

    def stop(self):
        if not self.isRunning:
            return

        self.isRunning = False
        self._stop_event.set()

        # Wait for thread to finish
        if self._pump_thread and self._pump_thread.is_alive():
            self._pump_thread.join(timeout=1.0)

        self.en_line.set_value(1)  # Disable motor driver

    def setFlowRate(self, flowRate: float):
        self.stepPeriod = flowRateToStepPeriod(flowRate)

    def getToggleSubject(self):
        return self.toggleSubject

    def _on_toggle_changed(self, is_on: bool):
        """Handle toggle state changes"""
        if is_on:
            self.start()
        else:
            self.stop()

    def _pump_continuously(self):
        """Internal method to run the pump continuously."""
        while not self._stop_event.is_set():
            # Step pulse
            self.step_line.set_value(1)
            time.sleep(self.stepPeriod / 2)
            self.step_line.set_value(0)
            time.sleep(self.stepPeriod / 2)

    def cleanup(self):
        """Clean up GPIO resources."""
        self.stop()
        try:
            self.step_line.release()
            self.dir_line.release()
            self.en_line.release()
        except:
            pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

    def __del__(self):
        """Destructor."""
        self.cleanup()
