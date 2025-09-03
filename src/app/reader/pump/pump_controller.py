import tkinter as tk

# Import the appropriate pump based on environment
import platform

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.sliding_toggle import ToggleSwitch

if platform.system() == "Windows":
    from src.app.reader.pump.dev_pump import DevPump as PumpClass
else:
    from src.app.reader.pump.pump import Pump as PumpClass


class PumpController:
    """
    A controller class that wraps a pump and provides UI integration with a toggle switch.
    This keeps the pump classes clean and focused on their core functionality.
    """

    def __init__(self, parent_widget, **pump_kwargs):
        """
        Initialize the PumpController with a pump and toggle switch.

        Args:
            parent_widget: The tkinter parent widget for the toggle switch
            **pump_kwargs: Additional arguments to pass to the pump constructor
        """
        self.parent_widget = parent_widget
        self.pump = PumpClass(**pump_kwargs)

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
        return self.pump.start()

    def stop(self):
        """Stop the pump"""
        return self.pump.stop()

    def setSpeed(self, speed: float):
        """Set pump speed"""
        return self.pump.setSpeed(speed)

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


# Example usage showing clean separation
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Clean Pump Controller Example")
    root.geometry("300x200")

    # Create pump controller - pump stays clean, UI layer handles integration
    controller = PumpController(root)

    # Build UI
    main_frame = tk.Frame(root)
    main_frame.pack(padx=20, pady=20)

    # Title
    tk.Label(main_frame, text="Pump Control", font=("Arial", 14, "bold")).pack(pady=(0, 20))

    # Toggle from controller
    toggle_frame = tk.Frame(main_frame)
    toggle_frame.pack(pady=10)

    tk.Label(toggle_frame, text="Power:").pack(side=tk.LEFT, padx=(0, 10))
    controller.getToggle().pack(side=tk.LEFT)

    # Speed control
    speed_frame = tk.Frame(main_frame)
    speed_frame.pack(pady=20)

    tk.Label(speed_frame, text="Speed:").pack()

    speed_var = tk.DoubleVar(value=0.001)
    speed_scale = tk.Scale(
        speed_frame,
        variable=speed_var,
        from_=0.0001,
        to=0.01,
        resolution=0.0001,
        orient=tk.HORIZONTAL,
        length=200,
        command=lambda v: controller.setSpeed(float(v))
    )
    speed_scale.pack(pady=5)

    # Status display
    status_label = tk.Label(main_frame, text="Status: OFF", font=("Arial", 12))
    status_label.pack(pady=10)

    # Cleanup on close
    def on_closing():
        controller.cleanup()
        root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_closing)

    print("Clean architecture: Pump handles hardware, Controller handles UI integration")
    root.mainloop()