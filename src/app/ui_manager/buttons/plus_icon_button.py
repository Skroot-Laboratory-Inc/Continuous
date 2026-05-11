import tkinter as tk
from typing import Callable

from PIL import Image, ImageDraw, ImageTk

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.image_theme import ImageTheme


class PlusIconButton:
    """Code-drawn plus icon button.

    Rendered with PIL at supersampled resolution and downscaled with LANCZOS
    for crisp rounded caps.
    """

    SUPER_SAMPLE = 4
    STROKE_RATIO = 0.18
    INSET_RATIO = 0.0
    LIGHT_BG_COLOR = "#BFBFBF"
    DISABLED_COLOR = "#E5E5E5"

    def __init__(self, master, invokeFn: Callable):
        self.invokeFn = invokeFn
        self.width, self.height = ImageTheme().plusSize
        self._bg = Colors().body.background

        enabledColor = self.LIGHT_BG_COLOR if self._isLightBg() else Colors().buttons.background
        self.enabledImage: tk.PhotoImage = self._render(enabledColor)
        self.disabledImage: tk.PhotoImage = self._render(self.DISABLED_COLOR)

        self.button = tk.Button(
            master,
            bg=self._bg,
            activebackground=self._bg,
            highlightthickness=0,
            borderwidth=0,
            padx=0,
            pady=0,
            relief='flat',
            image=self.enabledImage,
            command=lambda: self.invoke())

    def _render(self, color: str) -> tk.PhotoImage:
        ss = self.SUPER_SAMPLE
        w, h = self.width * ss, self.height * ss
        inset = int(min(w, h) * self.INSET_RATIO)
        stroke = int(min(w, h) * self.STROKE_RATIO)

        img = Image.new("RGBA", (w, h), self._hexToRgba(self._bg))
        draw = ImageDraw.Draw(img)
        cx, cy = w // 2, h // 2
        radius = stroke // 2

        draw.rounded_rectangle(
            (inset, cy - stroke // 2, w - inset, cy + stroke // 2),
            radius=radius, fill=color)
        draw.rounded_rectangle(
            (cx - stroke // 2, inset, cx + stroke // 2, h - inset),
            radius=radius, fill=color)

        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    @staticmethod
    def _hexToRgba(hexColor: str):
        h = hexColor.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

    def _isLightBg(self) -> bool:
        h = self._bg.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return (0.299 * r + 0.587 * g + 0.114 * b) > 128

    def invoke(self):
        self.button["state"] = "disabled"
        self.button.configure(image=self.disabledImage)
        self.invokeFn()
        self.button["state"] = "normal"
        self.button.configure(image=self.enabledImage)

    def hide(self):
        self.button["state"] = "disabled"
        self.button.configure(image=self.disabledImage)
        self.button.grid_remove()

    def show(self):
        self.button["state"] = "normal"
        self.button.configure(image=self.enabledImage)
        self.button.grid()
        self.button.tkraise()
