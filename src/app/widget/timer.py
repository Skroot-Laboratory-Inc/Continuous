import math
import time
import tkinter as tk

from src.app.ui_manager.theme import Colors
from src.app.ui_manager.theme.font_theme import FontTheme


class RunningTimer:
    def __init__(self, frame, font=None):
        self.defaultFont = FontTheme().primary
        if font is None:
            font = self.defaultFont
        self.startTime = time.time()
        self.timer = tk.Label(frame, text="0h 0m 0s", font=font, background=Colors().body.background, foreground=Colors().body.text)
        self.frame = frame

    def resetTimer(self):
        self.startTime = time.time()
        self.timer.configure(text="0h 0m 0s", font=self.defaultFont, background=Colors().body.background, foreground=Colors().body.text)

    def updateTime(self, font=None):
        if font is None:
            font = self.defaultFont
        elapsed = (time.time() - self.startTime)
        hours = math.floor(elapsed / 3600)
        minutes = math.floor((elapsed % 3600) / 60)
        seconds = math.floor((elapsed % 3600) % 60)
        timeString = f"{hours}h {minutes}m {seconds}s"
        self.timer.configure(text=timeString, font=font)
