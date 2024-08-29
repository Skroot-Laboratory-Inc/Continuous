import math
import time
import tkinter as tk

from src.app.theme.font_theme import FontTheme


class RunningTimer:
    def __init__(self):
        self.startTime = None
        self.timer = None
        self.defaultFont = FontTheme().primary

    def createWidget(self, frame, font=None, backgroundColor='white', foregroundColor='black'):
        if font is None:
            font = self.defaultFont
        self.startTime = time.time()
        self.timer = tk.Label(frame, text="0h 0m 0s", font=font, background=backgroundColor, foreground=foregroundColor)
        self.packWidget()

    def packWidget(self):
        self.timer.pack(side='top', anchor='ne')

    def updateTime(self, font=None, backgroundColor='white', foregroundColor='black'):
        if font is None:
            font = self.defaultFont
        elapsed = (time.time() - self.startTime)
        hours = math.floor(elapsed / 3600)
        minutes = math.floor((elapsed % 3600) / 60)
        seconds = math.floor((elapsed % 3600) % 60)
        timeString = f"{hours}h {minutes}m {seconds}s"
        self.timer.configure(text=timeString, font=font, background=backgroundColor, foreground=foregroundColor)
