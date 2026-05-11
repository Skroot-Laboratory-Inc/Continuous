import tkinter as tk
from typing import Callable

from PIL import Image, ImageDraw, ImageTk

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.image_theme import ImageTheme


class SubmitArrowButton:
    """Code-drawn arrow icon button.

    Renders a right-pointing arrow with rounded line caps via PIL at
    supersampled resolution and downscales with LANCZOS for crisp edges.
    The underlying tk.Button's `configure` is intercepted so existing call
    sites that set `state='disabled'` automatically swap to the faded glyph.
    """

    SUPER_SAMPLE = 4
    STROKE_RATIO = 0.14
    ARM_BACK_X_RATIO = 0.50
    DISABLED_COLOR = "#E5E5E5"

    def __init__(self, master, invokeFn: Callable):
        self.invokeFn = invokeFn
        self.width, self.height = ImageTheme().arrowSize
        self._bg = Colors().body.background

        self.enabledImage: tk.PhotoImage = self._render(Colors().buttons.background)
        self.disabledImage: tk.PhotoImage = self._render(self.DISABLED_COLOR)

        self.button = tk.Button(
            master,
            bg=self._bg,
            activebackground=self._bg,
            highlightthickness=0,
            borderwidth=0,
            image=self.enabledImage,
            command=lambda: self.invoke())
        self._patchConfigure()

    def _render(self, color: str) -> tk.PhotoImage:
        ss = self.SUPER_SAMPLE
        w, h = self.width * ss, self.height * ss
        stroke = max(int(min(w, h) * self.STROKE_RATIO), 2)
        radius = stroke // 2

        tip_x = w - radius
        tip_y = h // 2
        back_x = int(w * self.ARM_BACK_X_RATIO)
        top_y = radius
        bot_y = h - radius
        shaft_start_x = radius

        img = Image.new("RGBA", (w, h), self._hexToRgba(self._bg))
        draw = ImageDraw.Draw(img)

        draw.line([(shaft_start_x, tip_y), (tip_x, tip_y)], fill=color, width=stroke)
        draw.line([(tip_x, tip_y), (back_x, top_y)], fill=color, width=stroke)
        draw.line([(tip_x, tip_y), (back_x, bot_y)], fill=color, width=stroke)

        for cx, cy in [(shaft_start_x, tip_y), (tip_x, tip_y), (back_x, top_y), (back_x, bot_y)]:
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)

        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    @staticmethod
    def _hexToRgba(hexColor: str):
        h = hexColor.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

    def _patchConfigure(self):
        """Intercept state changes on the underlying tk.Button so the image
        is swapped automatically when call sites do `button.config(state=...)`.
        """
        original = self.button.configure

        def wrapped(cnf=None, **kw):
            if isinstance(cnf, dict):
                kw = {**cnf, **kw}
                cnf = None
            state = kw.get('state')
            if state is not None and 'image' not in kw:
                kw['image'] = self.enabledImage if str(state) == 'normal' else self.disabledImage
            return original(cnf, **kw) if cnf is not None else original(**kw)

        self.button.configure = wrapped
        self.button.config = wrapped

    def invoke(self):
        self.button["state"] = "disabled"
        self.invokeFn()
        self.button["state"] = "normal"

    def hide(self):
        self.button["state"] = "disabled"
        self.button.grid_remove()

    def show(self):
        self.button["state"] = "normal"
        self.button.grid()
        self.button.tkraise()
