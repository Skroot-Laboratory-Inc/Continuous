import tkinter as tk

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme


def createWidget(frame):
    global widget
    widget = tk.Label(frame, text="", wraplength=900)
    return widget


def getWidget():
    return widget


def setText(text, font=None, backgroundColor=None, foregroundColor=None):
    if font is None:
        font = FontTheme().textNotification
    if backgroundColor is None:
        backgroundColor = Colors().primaryColor
    if foregroundColor is None:
        foregroundColor = Colors().secondaryColor
    widget.configure(text=text, font=font, background=backgroundColor, foreground=foregroundColor)
