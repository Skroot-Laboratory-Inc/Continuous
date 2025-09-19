import os
import socket
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from typing import Callable

from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.helper_methods.ui_helpers import launchKeyboard, createDropdown
from src.app.model.setup_reader_form_input import SetupReaderFormInput
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.widget_theme import WidgetTheme


class SetupReaderForm:
    def __init__(self, rootManager: RootManager, guidedSetupInputs: SetupReaderFormInput, parent: tk.Frame,
                 submitFn: Callable):
        self.RootManager = rootManager
        self.parent = parent
        self.submitFn = submitFn
        self.Fonts = FontTheme()
        self.window = tk.Frame(parent, background=Colors().secondaryColor)
        self.guidedSetupResults = guidedSetupInputs
        self.calibrateRequired = tk.IntVar(value=1)
        self.setCalibrate()
        self.GlobalFileManager = None
        self.equilibrationTimeEntry = tk.StringVar(value=f'{guidedSetupInputs.getEquilibrationTime():g}')
        self.pumpFlowRateEntry = tk.StringVar(value=f"{guidedSetupInputs.getPumpFlowRate():g}")
        self.lotIdEntry = tk.StringVar(value=guidedSetupInputs.getLotId())
        self.deviceIdEntry = tk.StringVar(value=socket.gethostname())
        self.monthEntry = tk.IntVar(value=guidedSetupInputs.getMonth())
        self.dayEntry = tk.IntVar(value=guidedSetupInputs.getDay())
        self.yearEntry = tk.IntVar(value=guidedSetupInputs.getYear())
        self.scanRateEntry = tk.StringVar(value=f'{guidedSetupInputs.getScanRate():g}')
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.pack(fill="x", expand=True)

        ''' Normal entries '''
        entriesMap = {}
        row = 0

        entriesMap['Device ID'] = tk.Entry(
            self.window,
            textvariable=self.deviceIdEntry,
            borderwidth=0,
            font=self.Fonts.primary,
            highlightthickness=0,
            justify="center")

        entriesMap['Run ID'] = tk.Entry(
            self.window,
            textvariable=self.lotIdEntry,
            borderwidth=0,
            font=self.Fonts.primary,
            highlightthickness=0,
            justify="center")

        entriesMap['Pump Flow Rate (mL/hr)'] = tk.Entry(
            self.window,
            textvariable=self.pumpFlowRateEntry,
            borderwidth=0,
            font=self.Fonts.primary,
            highlightthickness=0,
            justify="center")

        options = ["2", "5", "10"]
        entriesMap["Scan Rate (min)"] = createDropdown(self.window, self.scanRateEntry, options)

        options = ["0", "0.2", "2", "12", "24"]
        entriesMap["Equilibration Time (hr)"] = createDropdown(self.window, self.equilibrationTimeEntry, options)

        ''' Create Label and Entry Widgets'''
        for entryLabelText, entry in entriesMap.items():

            tk.Label(self.window, text=entryLabelText, bg='white', font=self.Fonts.primary).grid(row=row,
                                                                                                       column=0,
                                                                                                       sticky='w')
            entry.grid(row=row, column=1, sticky="ew", ipady=WidgetTheme().internalPadding)
            if entryLabelText == "Run ID":
                entry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, self.RootManager.getRoot(), "Run ID:  "))
            if entryLabelText == "Pump Flow Rate (mL/hr)":
                entry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, self.RootManager.getRoot(), "Flow Rate:  "))
            if entryLabelText == "Device ID":
                entry['state'] = "disabled"
                entry['disabledbackground'] = Colors().secondaryColor
            row += 1
            ttk.Separator(self.window, orient="horizontal").grid(row=row, column=1, sticky="ew")
            row += 1

        calibrateCheck = tk.Checkbutton(self.window,
                                        text="Calibration Required",
                                        variable=self.calibrateRequired,
                                        font=self.Fonts.primary,
                                        onvalue=1,
                                        offvalue=0,
                                        pady=WidgetTheme().externalPadding,
                                        command=self.setCalibrate,
                                        bg='white', borderwidth=0, highlightthickness=0)
        calibrateCheck.grid(row=row, column=1, sticky="w")

        self.submitButton = GenericButton("Submit", self.window, self.onSubmit).button
        row += 1
        self.submitButton.grid(row=row, column=0, sticky="sw")
        self.cancelButton = GenericButton("Cancel", self.window, self.onCancel).button
        self.cancelButton.grid(row=row, column=1, sticky="se")

    def getConfiguration(self) -> (SetupReaderFormInput, GlobalFileManager):
        return self.guidedSetupResults, self.GlobalFileManager

    def setCalibrate(self):
        if self.calibrateRequired.get() == 1:
            self.guidedSetupResults.calibrate = True
        if self.calibrateRequired.get() == 0:
            self.guidedSetupResults.calibrate = False

    def onCancel(self):
        self.parent.grid_remove()

    def updateConfiguration(self):
        guidedSetupInputs = self.guidedSetupResults.resetRun()
        self.lotIdEntry.set(guidedSetupInputs.getLotId())
        self.monthEntry.set(guidedSetupInputs.getMonth())
        self.dayEntry.set(guidedSetupInputs.getDay())
        self.yearEntry.set(guidedSetupInputs.getYear())
        self.pumpFlowRateEntry.set(guidedSetupInputs.getPumpFlowRate())
        return self.guidedSetupResults

    def resetFlowRate(self):
        guidedSetupInputs = self.guidedSetupResults.resetFlowRate()
        self.pumpFlowRateEntry.set(guidedSetupInputs.getPumpFlowRate())
        return self.guidedSetupResults

    def onSubmit(self):
        if self.monthEntry.get() != "" and self.dayEntry.get() != "" and self.yearEntry.get() != "" and self.lotIdEntry.get() != "":
            self.guidedSetupResults.equilibrationTime = float(self.equilibrationTimeEntry.get())
            self.guidedSetupResults.scanRate = float(self.scanRateEntry.get())
            self.guidedSetupResults.pumpFlowRate = float(self.pumpFlowRateEntry.get())
            self.guidedSetupResults.month = self.monthEntry.get()
            self.guidedSetupResults.day = self.dayEntry.get()
            self.guidedSetupResults.year = self.yearEntry.get()
            self.guidedSetupResults.lotId = self.lotIdEntry.get()
            self.guidedSetupResults.deviceId = self.deviceIdEntry.get()
            self.guidedSetupResults.savePath = self.createSavePath(self.guidedSetupResults.getDate())
            self.GlobalFileManager = GlobalFileManager(self.guidedSetupResults.savePath)
            self.parent.grid_remove()
            self.submitFn()
        else:
            messagebox.showerror(
                "Incorrect Formatting",
                "One (or more) of the values entered is not formatted properly")

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
