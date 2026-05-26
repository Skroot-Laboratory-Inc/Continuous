import logging
import tkinter as tk

from PIL import Image, ImageDraw, ImageTk

from src.app.use_case.flow_cell.pump.pump_helpers import rpmToActualFlowRate
from src.app.use_case.flow_cell.pump.pump_manager import PumpManager
from src.app.ui_manager.theme.colors import Colors


class _ModernSlider(tk.Canvas):
    """
    Canvas-drawn horizontal slider with a thin trough and a large circular
    thumb, for a modern (iOS/Material-style) look. ttk.Scale's appearance is
    largely theme-controlled and ignores most style options on Windows, so a
    small custom Canvas gives us precise control instead.

    Drawing is done with Pillow at 2x supersampling and downsampled with
    LANCZOS so the thumb circle and rounded trough ends are anti-aliased --
    tk.Canvas's native shape drawing is not.
    """

    TROUGH_HEIGHT = 5
    THUMB_RADIUS = 20
    HEIGHT = 48
    SUPERSAMPLE = 2

    def __init__(self, parent, fromValue, toValue,
                 troughColor, fillColor, thumbColor, thumbBorderColor,
                 bg, onChange=None, onRelease=None):
        super().__init__(parent, height=self.HEIGHT, bg=bg,
                         highlightthickness=0, bd=0)
        self.fromValue = fromValue
        self.toValue = toValue
        self.value = fromValue
        self.bgColor = bg
        self.troughColor = troughColor
        self.fillColor = fillColor
        self.thumbColor = thumbColor
        self.thumbBorderColor = thumbBorderColor
        self.onChange = onChange
        self.onRelease = onRelease
        self._photo = None
        self._imageId = None

        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Button-1>", self._onClickOrDrag)
        self.bind("<B1-Motion>", self._onClickOrDrag)
        self.bind("<ButtonRelease-1>", self._onRelease)

    def _padding(self) -> int:
        return self.THUMB_RADIUS + 2

    def _bounds(self):
        pad = self._padding()
        x0 = pad
        x1 = max(pad + 1, self.winfo_width() - pad)
        return x0, x1

    def _valueToX(self, value: float) -> float:
        x0, x1 = self._bounds()
        span = self.toValue - self.fromValue
        ratio = ((value - self.fromValue) / span) if span else 0.0
        ratio = max(0.0, min(1.0, ratio))
        return x0 + ratio * (x1 - x0)

    def _xToValue(self, x: float) -> float:
        x0, x1 = self._bounds()
        ratio = max(0.0, min(1.0, (x - x0) / (x1 - x0)))
        return self.fromValue + ratio * (self.toValue - self.fromValue)

    def _redraw(self):
        try:
            w = self.winfo_width()
            h = self.winfo_height()
            if w <= 1 or h <= 1:
                return

            s = self.SUPERSAMPLE
            img = Image.new("RGB", (w * s, h * s), self.bgColor)
            draw = ImageDraw.Draw(img)

            cy = (h * s) // 2
            pad = self._padding() * s
            x0 = pad
            x1 = w * s - pad
            th = self.TROUGH_HEIGHT * s
            ty0 = cy - th // 2
            ty1 = ty0 + th
            radius = th // 2

            draw.rounded_rectangle((x0, ty0, x1, ty1), radius=radius, fill=self.troughColor)
            thumbX = int(round(self._valueToX(self.value) * s))
            if thumbX > x0:
                draw.rounded_rectangle((x0, ty0, thumbX, ty1), radius=radius, fill=self.fillColor)
            r = self.THUMB_RADIUS * s
            draw.ellipse(
                (thumbX - r, cy - r, thumbX + r, cy + r),
                fill=self.thumbColor,
                outline=self.thumbBorderColor,
                width=max(1, 2 * s),
            )

            img = img.resize((w, h), Image.LANCZOS)
            self._photo = ImageTk.PhotoImage(img)
            if self._imageId is None:
                self._imageId = self.create_image(0, 0, image=self._photo, anchor="nw")
            else:
                self.itemconfigure(self._imageId, image=self._photo)
        except Exception:
            logging.exception("Failed to redraw slider", extra={"id": "UI failure"})

    def _onClickOrDrag(self, event):
        try:
            self.value = self._xToValue(event.x)
            self._redraw()
            if self.onChange:
                self.onChange(self.value)
        except Exception:
            logging.exception("Slider drag failed", extra={"id": "UI failure"})

    def _onRelease(self, _event):
        try:
            if self.onRelease:
                self.onRelease(self.value)
        except Exception:
            logging.exception("Slider release failed", extra={"id": "UI failure"})

    def setValue(self, value: float):
        self.value = max(self.fromValue, min(self.toValue, value))
        self._redraw()

    def getValue(self) -> float:
        return self.value


class FlowRateSliderWidget:
    """
    Slider that lets the user select a pump flow rate during a run, ranging
    from the minimum pump speed up to the priming speed. Moving the slider
    immediately updates the pump's flow rate when the pump is running.
    """

    SNAP_RPM = 0.4  # ~1 mL/hr at the linear end of the curve

    def __init__(self, parentWidget: tk.Widget, pumpManager: PumpManager):
        self.parentWidget = parentWidget
        self.pumpManager = pumpManager

        self.minRate = pumpManager.getMinRpm()
        self.maxRate = pumpManager.getMaxRpm()

        colors = Colors()
        bg = colors.body.background
        text = colors.body.text
        trough = getattr(colors.body, "secondary_background", bg)
        accent = getattr(colors.buttons, "background", text)
        accentBorder = getattr(colors.buttons, "border", accent)

        self.frame = tk.Frame(parentWidget, bg=bg)
        self.frame.grid_columnconfigure(1, weight=1)

        self.valueLabel = tk.Label(
            self.frame,
            text=self._formatLabel(self.minRate),
            bg=bg,
            fg=text,
        )
        self.valueLabel.grid(row=0, column=0, columnspan=3, sticky="w")

        tk.Label(self.frame, text="Low Flow", bg=bg, fg=text).grid(
            row=1, column=0, sticky="w", padx=(0, 8)
        )

        self.slider = _ModernSlider(
            self.frame,
            fromValue=self.minRate,
            toValue=self.maxRate,
            troughColor=trough,
            fillColor=accent,
            thumbColor=accent,
            thumbBorderColor=accentBorder,
            bg=bg,
            onChange=self._onSliderChange,
            onRelease=self._onSliderRelease,
        )
        self.slider.grid(row=1, column=1, sticky="ew", pady=4)
        self.slider.setValue(self.minRate)

        tk.Label(self.frame, text="High Flow", bg=bg, fg=text).grid(
            row=1, column=2, sticky="e", padx=(8, 0)
        )

    def _formatLabel(self, rpm) -> str:
        return f"Flow rate: ~{rpmToActualFlowRate(float(rpm)):.0f} mL/hr"

    def _snap(self, rpm: float) -> float:
        steps = round((rpm - self.minRate) / self.SNAP_RPM)
        snapped = self.minRate + steps * self.SNAP_RPM
        return max(self.minRate, min(self.maxRate, snapped))

    def _onSliderChange(self, rpm: float):
        try:
            self.valueLabel.config(text=self._formatLabel(self._snap(rpm)))
        except Exception:
            logging.exception("Failed to update flow rate label", extra={"id": "Reader"})

    def _onSliderRelease(self, rpm: float):
        try:
            snapped = self._snap(rpm)
            self.slider.setValue(snapped)
            self.valueLabel.config(text=self._formatLabel(snapped))
            self.pumpManager.setRpm(snapped)
        except Exception:
            logging.exception("Failed to apply flow rate from slider", extra={"id": "Reader"})

    def getWidget(self):
        return self.frame

    def reset(self):
        self.slider.setValue(self.minRate)
        self.valueLabel.config(text=self._formatLabel(self.minRate))
        self.pumpManager.setRpm(self.minRate)
