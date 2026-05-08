import logging
import tkinter as tk

from src.app.use_case.flow_cell.pump.pump_helpers import rpmToFlowRate
from src.app.use_case.flow_cell.pump.pump_manager import PumpManager
from src.app.ui_manager.theme.colors import Colors


class FlowRateSliderWidget:
    """
    Slider that lets the user select a pump flow rate during a run, ranging
    from the minimum pump speed up to the priming speed. Moving the slider
    immediately updates the pump's flow rate when the pump is running.
    """

    SNAP_RPM = 0.4  # 1 mL/hr

    def __init__(self, parentWidget: tk.Widget, pumpManager: PumpManager):
        self.parentWidget = parentWidget
        self.pumpManager = pumpManager

        self.minRate = pumpManager.getMinSpeed()
        self.maxRate = pumpManager.getMaxSpeed()

        self.frame = tk.Frame(parentWidget, bg=Colors().body.background)
        self.frame.grid_columnconfigure(1, weight=1)

        self.valueLabel = tk.Label(
            self.frame,
            text=self._formatLabel(self.minRate),
            bg=Colors().body.background,
            fg=Colors().body.text,
        )
        self.valueLabel.grid(row=0, column=0, columnspan=3, sticky="w")

        tk.Label(
            self.frame,
            text="Low Flow",
            bg=Colors().body.background,
            fg=Colors().body.text,
        ).grid(row=1, column=0, sticky="w", padx=(0, 5))

        outlineFrame = tk.Frame(self.frame, bg=Colors().body.text)
        outlineFrame.grid(row=1, column=1, sticky="nsew")
        outlineFrame.grid_columnconfigure(0, weight=1)
        outlineFrame.grid_rowconfigure(0, weight=1)

        self.scale = tk.Scale(
            outlineFrame,
            from_=self.minRate,
            to=self.maxRate,
            resolution=self.SNAP_RPM,
            orient=tk.HORIZONTAL,
            showvalue=False,
            command=self._onSliderChange,
            bg=Colors().body.text,
            fg=Colors().body.text,
            troughcolor=Colors().body.background,
            activebackground=Colors().body.text,
            highlightthickness=0,
            bd=0,
            width=50,
            sliderlength=60,
        )
        self.scale.set(self.minRate)
        self.scale.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        self.scale.bind("<ButtonRelease-1>", self._onSliderRelease)

        tk.Label(
            self.frame,
            text="High Flow",
            bg=Colors().body.background,
            fg=Colors().body.text,
        ).grid(row=1, column=2, sticky="e", padx=(5, 0))

    def _formatLabel(self, rpm) -> str:
        return f"Flow rate: {rpmToFlowRate(float(rpm)):.0f} mL/hr"

    def _onSliderChange(self, value: str):
        try:
            rpm = float(value)
            self.valueLabel.config(text=self._formatLabel(rpm))
        except Exception:
            logging.exception("Failed to update flow rate label", extra={"id": "Reader"})

    def _onSliderRelease(self, _event):
        try:
            rpm = float(self.scale.get())
            self.pumpManager.setFlowRate(rpm)
        except Exception:
            logging.exception("Failed to apply flow rate from slider", extra={"id": "Reader"})

    def getWidget(self):
        return self.frame

    def reset(self):
        self.scale.set(self.minRate)
        self.pumpManager.setFlowRate(self.minRate)
