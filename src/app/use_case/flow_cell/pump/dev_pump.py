from reactivex.subject import BehaviorSubject

from src.app.use_case.flow_cell.pump.pump_interface import PumpInterface


class DevPump(PumpInterface):
    def __init__(self):
        self.isRunning = False
        self.speed = 0.001
        self.toggleSubject = BehaviorSubject(False)  # Start with pump off
        self.toggleSubject.subscribe(self._on_toggle_changed)

    def start(self) -> str:
        """Start the pump (mock implementation for dev environment)"""
        if not self.isRunning:
            self.isRunning = True
            print("DevPump: Starting pump")
            return "Pump started"
        return "Pump already running"

    def stop(self):
        """Stop the pump (mock implementation for dev environment)"""
        if self.isRunning:
            self.isRunning = False
            print("DevPump: Stopping pump")

    def setFlowRate(self, speed: float):
        """Set pump speed (mock implementation for dev environment)"""
        self.speed = speed
        print(f"DevPump: Flow Rate set to {speed}")

    def getToggleSubject(self):
        """Get the BehaviorSubject for toggle integration"""
        return self.toggleSubject

    def _on_toggle_changed(self, is_on: bool):
        """Handle toggle state changes"""
        if is_on:
            self.start()
        else:
            self.stop()
