import os
import socket
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

import pyautogui

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.model.guided_setup_input import GuidedSetupInput
from src.app.ui_manager.root_manager import RootManager


class SetupForm:
    def __init__(self, rootManager: RootManager, guidedSetupInputs: GuidedSetupInput):
        self.RootManager = rootManager
        self.window = self.RootManager.createTopLevel()
        self.entrySize = 10
        self.guidedSetupResults = guidedSetupInputs
        self.calibrateRequired = tk.IntVar(value=1)
        self.setCalibrate()
        self.equilibrationTimeEntry = tk.StringVar(value=f'{guidedSetupInputs.getEquilibrationTime():g}')
        self.lotIdEntry = tk.StringVar(value=guidedSetupInputs.getLotId())
        self.incubatorEntry = tk.StringVar(value=guidedSetupInputs.getIncubator())
        self.monthEntry = tk.IntVar(value=guidedSetupInputs.getMonth())
        self.dayEntry = tk.IntVar(value=guidedSetupInputs.getDay())
        self.yearEntry = tk.IntVar(value=guidedSetupInputs.getYear())
        self.scanRateEntry = tk.StringVar(value=f'{guidedSetupInputs.getScanRate():g}')
        self.window.grid_columnconfigure(1, weight=1)
        self.window.minsize(200, 200)
        w = self.window.winfo_reqwidth()
        h = self.window.winfo_reqheight()
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.window.geometry('+%d+%d' % (x, y))
        self.RootManager.raiseAboveRoot(self.window)

        ''' MM DD YYYY Date entry '''
        dateFrame = tk.Frame(self.window, bg='white')
        tk.Spinbox(dateFrame,
                   textvariable=self.monthEntry,
                   width=round(self.entrySize / 4),
                   from_=1,
                   to=12,
                   borderwidth=0,
                   highlightthickness=0).grid(row=0, column=1)
        tk.Label(dateFrame,
                 text="/",
                 bg='white',
                 width=round(self.entrySize / 10)).grid(row=0, column=2)
        tk.Spinbox(dateFrame,
                   textvariable=self.dayEntry,
                   width=round(self.entrySize / 4),
                   from_=1,
                   to=31,
                   borderwidth=0,
                   highlightthickness=0).grid(row=0, column=3)
        tk.Label(dateFrame,
                 text="/", bg='white',
                 width=round(self.entrySize / 10)).grid(row=0, column=4)
        tk.Spinbox(dateFrame,
                   textvariable=self.yearEntry,
                   width=round(self.entrySize / 2),
                   from_=2023,
                   to=2050,
                   borderwidth=0,
                   highlightthickness=0).grid(row=0, column=5)

        ''' Normal entries '''
        entriesMap = {}
        row = 0

        entriesMap['Date'] = dateFrame

        entriesMap['Lot ID'] = tk.Entry(
            self.window,
            textvariable=self.lotIdEntry,
            borderwidth=0,
            highlightthickness=0,
            justify="center")

        entriesMap['Incubator'] = tk.Entry(
            self.window,
            textvariable=self.incubatorEntry,
            borderwidth=0,
            highlightthickness=0,
            justify="center")

        options = ["2", "5", "10"]
        entriesMap["Scan Rate (min)"] = createDropdown(self.window, self.scanRateEntry, options, True)

        options = ["0", "0.2", "2", "12", "24"]
        entriesMap["Equilibration Time (hr)"] = createDropdown(self.window, self.equilibrationTimeEntry, options, True)

        ''' Create Label and Entry Widgets'''
        for entryLabelText, entry in entriesMap.items():
            tk.Label(self.window, text=entryLabelText, bg='white').grid(row=row, column=0, sticky='w')
            entry.grid(row=row, column=1, sticky="ew")
            row += 1
            ttk.Separator(self.window, orient="horizontal").grid(row=row, column=1, sticky="ew")
            row += 1

        ''' Create Spacer between entries and submit option '''
        spacer = tk.Entry(self.window, borderwidth=0, highlightthickness=0, disabledbackground="white", cursor='arrow')
        row += 1
        spacer.grid(row=row, column=1, sticky="ew")
        spacer['state'] = "disabled"

        var = tk.Checkbutton(self.window,
                             text="Calibration Required",
                             variable=self.calibrateRequired,
                             onvalue=1,
                             offvalue=0,
                             command=self.setCalibrate,
                             bg='white', borderwidth=0, highlightthickness=0)
        var.grid(row=row, column=1, sticky="ew")

        self.submitButton = ttk.Button(self.window, text="Submit", command=lambda: self.onSubmit(), style='Default.TButton')
        row += 1
        self.submitButton.grid(row=row, column=0, sticky="sw")
        self.RootManager.waitForWindow(self.window)

    def getConfiguration(self) -> (GuidedSetupInput, GlobalFileManager):
        return self.guidedSetupResults, self.GlobalFileManager

    def setCalibrate(self):
        if self.calibrateRequired.get() == 1:
            self.guidedSetupResults.calibrate = True
        if self.calibrateRequired.get() == 0:
            self.guidedSetupResults.calibrate = False

    def onSubmit(self):
        if self.monthEntry.get() != "" and self.dayEntry.get() != "" and self.yearEntry.get() != "" and self.lotIdEntry.get() != "":
            self.guidedSetupResults.equilibrationTime = float(self.equilibrationTimeEntry.get())
            self.guidedSetupResults.scanRate = float(self.scanRateEntry.get())
            self.guidedSetupResults.month = self.monthEntry.get()
            self.guidedSetupResults.day = self.dayEntry.get()
            self.guidedSetupResults.year = self.yearEntry.get()
            self.guidedSetupResults.lotId = self.lotIdEntry.get()
            self.guidedSetupResults.incubator = self.incubatorEntry.get()
            self.guidedSetupResults.savePath = self.createSavePath(self.guidedSetupResults.getDate())
            self.GlobalFileManager = GlobalFileManager(self.guidedSetupResults.savePath)
            self.takeScreenshot()
            self.window.destroy()
        else:
            messagebox.showerror(
                "Incorrect Formatting",
                "One (or more) of the values entered is not formatted properly")
            self.window.tkraise()

    def createSavePath(self, date):
        FileManager = CommonFileManager()
        baseSavePath = FileManager.getDataSavePath()
        if not os.path.exists(baseSavePath):
            os.mkdir(baseSavePath)
        if not os.path.exists(
                f"{baseSavePath}/{date}_{self.lotIdEntry.get()}"):
            return f"{baseSavePath}/{date}_{self.lotIdEntry.get()}"
        else:
            incrementalNumber = 0
            while os.path.exists(
                    f"{baseSavePath}/{date}_{self.lotIdEntry.get()} ({incrementalNumber})"):
                incrementalNumber += 1
            return f"{baseSavePath}/{date}_{self.lotIdEntry.get()} ({incrementalNumber})"

    def takeScreenshot(self):
        x, y = self.window.winfo_rootx(), self.window.winfo_rooty()
        w, h = self.window.winfo_width(), self.window.winfo_height()
        if not os.path.exists(os.path.dirname(self.guidedSetupResults.savePath)):
            os.mkdir(os.path.dirname(self.guidedSetupResults.savePath))
        if not os.path.exists(self.guidedSetupResults.savePath):
            os.mkdir(self.guidedSetupResults.savePath)
        im = pyautogui.screenshot(region=(x, y, w, round(h * 0.77)))
        im.save(self.GlobalFileManager.getSetupForm())


def createDropdown(root, entryVariable, options, addSpace):
    if addSpace:
        options = [f"             {option}             " for option in options]
    scanRateValue = entryVariable.get()
    optionMenu = tk.OptionMenu(root, entryVariable, *options)
    optionMenu.config(bg="white", borderwidth=0, highlightthickness=0, indicatoron=False)
    optionMenu["menu"].config(bg="white")
    entryVariable.set(scanRateValue)
    return optionMenu
