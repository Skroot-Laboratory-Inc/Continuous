import datetime
import tkinter as tk

from src.app.helper_methods.ui_helpers import datetimeToDisplay
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme


class HarvestText:
    def __init__(self, master):
        self.label = "Estimated Saturation Time"
        self.timeFrame = "No Estimate Available"
        self.postFix = ""
        self.finalSaturationTime = 0
        self.isSaturated = False
        self.timeAfterSaturation = 0
        self.text = tk.Label(
            master,
            text=f"{self.label}: {self.timeFrame}",
            font=FontTheme().primary2,
            background=Colors().secondaryColor,
            foreground=Colors().primaryColor)

    def isNowSaturated(self, currentTime):
        if not self.isSaturated:
            self.postFix = f"Time Elapsed Since Saturation: {self.timeAfterSaturation}"
            self.label = "Final Saturation Time"
            self.finalSaturationTime = currentTime
            self.timeFrame = datetimeToDisplay(datetime.datetime.now())
            self.isSaturated = True
            self.updateText()

    def updateSaturationTime(self, saturationTime, currentTime):
        self.text.configure(font=FontTheme().primaryBoldUnderlined)
        if not self.isSaturated:
            hoursFromNowStart = int((saturationTime-currentTime)*0.8)
            minutesFromNowStart = round((saturationTime-currentTime)*0.8*60) % 60
            hoursFromNowEnd = int((saturationTime-currentTime)*1.2)
            minutesFromNowEnd = round((saturationTime-currentTime)*1.2*60) % 60
            startTimeChange = datetime.timedelta(hours=hoursFromNowStart, minutes=minutesFromNowStart)
            endTimeChange = datetime.timedelta(hours=hoursFromNowEnd, minutes=minutesFromNowEnd)
            startTime = datetime.datetime.now() + startTimeChange
            endTime = datetime.datetime.now() + endTimeChange
            if startTime > datetime.datetime.now():
                self.timeFrame = f"{datetimeToDisplay(startTime)} - {datetimeToDisplay(endTime)}"
            else:
                self.timeFrame = f"{datetimeToDisplay(datetime.datetime.now())} - {datetimeToDisplay(endTime)}"
        else:
            self.timeAfterSaturation = f"{int(currentTime - self.finalSaturationTime)} hrs {str(round((currentTime - self.finalSaturationTime)*60) % 60).zfill(2)} mins"
            self.postFix = f"Time Elapsed Since Saturation: {self.timeAfterSaturation}"
        self.updateText()

    def updateText(self):
        self.text.configure(text=f"{self.label}: {self.timeFrame}\n{self.postFix}")


