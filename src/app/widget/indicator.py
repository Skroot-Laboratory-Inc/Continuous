import tkinter as tk

from PIL import Image, ImageDraw, ImageTk

from src.app.ui_manager.theme.colors import Colors


def _renderIndicatorImage(diameter: int, border: int, fill: str, outline: str, bg: str) -> ImageTk.PhotoImage:
    """
    Render an indicator circle at 2x and downsample with LANCZOS so the edge
    is anti-aliased. tk.Canvas's native ellipse drawing is not anti-aliased,
    which leaves a jagged edge on the circle outline.
    """
    s = 2
    size = diameter * s
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    strokeWidth = max(1, border * s)
    inset = strokeWidth // 2
    draw.ellipse(
        (inset, inset, size - inset - 1, size - inset - 1),
        fill=fill,
        outline=outline,
        width=strokeWidth,
    )
    return ImageTk.PhotoImage(img.resize((diameter, diameter), Image.LANCZOS))


def createIndicatorOnCanvas(canvas: tk.Canvas, diameter: int, border: int,
                            fill: str, outline: str, bg: str) -> int:
    """
    Render the indicator circle onto the given canvas as an anti-aliased image
    and return the canvas item id. Geometry parameters are stored on the
    canvas so :class:`Indicator` can re-render with a new fill color.
    """
    photo = _renderIndicatorImage(diameter, border, fill, outline, bg)
    canvas._indicatorPhoto = photo
    canvas._indicatorDiameter = diameter
    canvas._indicatorBorder = border
    canvas._indicatorOutline = outline
    canvas._indicatorBg = bg
    return canvas.create_image(0, 0, image=photo, anchor="nw")


class Indicator:
    def __init__(self, readerNumber, readerPage):
        self.indicatorColor = Colors().status.success
        self.readerPage = readerPage
        self.readerNumber = readerNumber
        self.indicatorCanvas, self.indicator = self.readerPage.getIndicator()

    def _setFill(self, color: str):
        canvas = self.indicatorCanvas
        photo = _renderIndicatorImage(
            canvas._indicatorDiameter,
            canvas._indicatorBorder,
            color,
            canvas._indicatorOutline,
            canvas._indicatorBg,
        )
        canvas._indicatorPhoto = photo
        canvas.itemconfigure(self.indicator, image=photo)

    def changeIndicatorGreen(self):
        self._setFill(Colors().status.success)
        self.updateHarvestJson(Colors().status.success)

    def changeIndicatorYellow(self):
        self._setFill(Colors().status.warning)
        self.updateHarvestJson(Colors().status.warning)

    def changeIndicatorRed(self):
        self._setFill(Colors().status.error)
        self.updateHarvestJson(Colors().status.error)

    def updateHarvestJson(self, harvestColor):
        self.indicatorColor = harvestColor
