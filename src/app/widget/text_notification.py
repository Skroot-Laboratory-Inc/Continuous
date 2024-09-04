import tkinter as tk

from src.app.theme.font_theme import FontTheme


def createWidget(frame):
    global widget
    widget = tk.Label(frame, text="")


def packWidget():
    widget.pack(fill='x')


def setText(text, font=None, backgroundColor='RoyalBlue4', foregroundColor='white'):
    if font is None:
        font = FontTheme().primary
    widget.configure(text=text, font=font, background=backgroundColor, foreground=foregroundColor)
