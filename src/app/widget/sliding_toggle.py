import tkinter as tk

from PIL import Image, ImageDraw, ImageTk
from reactivex.subject import BehaviorSubject

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.image_theme import ImageTheme


class ToggleSwitch:
    """iOS-style sliding toggle bound to a ReactiveX BehaviorSubject.

    Rendered with PIL at supersampled resolution and downscaled with LANCZOS
    so the rounded edges stay smooth.
    """

    KNOB_PADDING = 3
    SUPER_SAMPLE = 4

    def __init__(
        self,
        parent: tk.Widget,
        behavior_subject: BehaviorSubject,
        size: tuple = None,
    ):
        """
        Create a toggle switch widget that works exclusively with ReactiveX BehaviorSubject

        Args:
            parent: The parent tkinter widget
            behavior_subject: ReactiveX BehaviorSubject that will receive toggle state changes
            size: Optional (width, height) override; defaults to ImageTheme().toggleSize
        """
        self.parent = parent
        self.behavior_subject = behavior_subject
        self.width, self.height = size if size is not None else ImageTheme().toggleSize
        self._bg = Colors().body.background
        self._enabled = True

        self.is_on = behavior_subject.value if hasattr(behavior_subject, 'value') else False

        self._images = {
            (on, enabled): self._render(on=on, enabled=enabled)
            for on in (True, False)
            for enabled in (True, False)
        }
        self.button = tk.Label(
            parent,
            bd=0,
            bg=self._bg,
            image=self._currentImage(),
            cursor="hand2",
        )
        self.button.bind("<Button-1>", self._onClick)

        self._subscription = self.behavior_subject.subscribe(self._on_external_state_change)

    def _render(self, on: bool, enabled: bool) -> ImageTk.PhotoImage:
        ss = self.SUPER_SAMPLE
        w, h = self.width * ss, self.height * ss
        knobPad = self.KNOB_PADDING * ss
        if not enabled:
            track = "#E5E5E5"
            knob = "#F5F5F5"
        elif on:
            track = Colors().buttons.background
            knob = "#FFFFFF"
        else:
            track = "#BFBFBF"
            knob = "#FFFFFF"

        img = Image.new("RGBA", (w, h), self._hexToRgba(self._bg))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=track)
        knobSize = h - 2 * knobPad
        knobX = (w - h + knobPad) if on else knobPad
        draw.ellipse(
            (knobX, knobPad, knobX + knobSize, knobPad + knobSize),
            fill=knob,
        )
        img = img.resize((self.width, self.height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    @staticmethod
    def _hexToRgba(hexColor: str):
        h = hexColor.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

    def _currentImage(self) -> ImageTk.PhotoImage:
        return self._images[(bool(self.is_on), self._enabled)]

    def _refresh(self):
        self.button.configure(image=self._currentImage())

    def _onClick(self, _event):
        if not self._enabled:
            return
        self.is_on = not self.is_on
        self._refresh()
        self.behavior_subject.on_next(self.is_on)

    def _on_external_state_change(self, new_state: bool):
        if new_state != self.is_on:
            self.is_on = new_state
            self._refresh()

    def setEnabled(self, enabled: bool):
        self._enabled = enabled
        self._refresh()

    def getWidget(self):
        """Get the underlying tkinter widget"""
        return self.button

    def get_state(self):
        """Get the current state of the toggle"""
        return self.is_on

    def set_state(self, state: bool):
        """
        Set the state of the toggle programmatically
        This will publish to the BehaviorSubject, maintaining reactive consistency
        """
        if state != self.is_on:
            self.behavior_subject.on_next(state)

    def cleanup(self):
        """Clean up the subscription when done"""
        self.is_on = False
        if hasattr(self, '_subscription'):
            self._subscription.dispose()

    def __del__(self):
        """Ensure cleanup happens"""
        self.cleanup()
