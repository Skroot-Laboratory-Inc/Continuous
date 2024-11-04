import tkinter as tk

from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme


def createWidget(frame):
    global widget
    widget = tk.Label(frame, text="")
    return widget


def setText(text, font=None, backgroundColor=None, foregroundColor=None):
    if font is None:
        font = FontTheme().primary
    if backgroundColor is None:
        backgroundColor = Colors().primaryColor
    if foregroundColor is None:
        foregroundColor = Colors().secondaryColor
    widget.configure(text=text, font=font, background=backgroundColor, foreground=foregroundColor)
