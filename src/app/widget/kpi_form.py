import tkinter as tk
from tkinter import ttk

from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager


class KpiForm:
    def __init__(self, parent: tk.Frame, rootManager: RootManager):
        """ Displays all relevant information for a scan to the user by placing them on the provided frame. """
        self.RootManager = rootManager
        self.sgi = tk.StringVar(value="-")
        self.lotId = tk.StringVar()
        self.saturationTime = tk.StringVar(value="No Estimate")
        self.user = tk.StringVar()

        self.parentFrame = parent
        row = self.addCommonLabels(0)
        self.addBarcodeLabels(row)

    def addCommonLabels(self, row):
        labelsMap = {}

        labelsMap["Saturation"] = tk.Label(
            self.parentFrame,
            font=FontTheme().primary,
            textvariable=self.saturationTime,
            bg='white')

        labelsMap['SGI'] = tk.Label(
            self.parentFrame,
            font=FontTheme().primary,
            textvariable=self.sgi,
            bg='white')

        for labelText, entry in labelsMap.items():
            tk.Label(self.parentFrame, text=labelText, bg='white', font=FontTheme().primary).grid(row=row, column=0, sticky='w', padx=10)
            entry.grid(row=row, column=1, sticky="ew")
            row += 1
            ttk.Separator(self.parentFrame, orient="horizontal").grid(row=row, column=1, sticky="ew")
            row += 1
        ttk.Separator(self.parentFrame, orient="horizontal").grid(row=row, column=0, pady=(0, 10))
        row += 1
        return row

    def addBarcodeLabels(self, row):
        labelsMap = {}
        if self.user != "":
            labelsMap['User'] = tk.Label(
                self.parentFrame,
                font=FontTheme().primary,
                textvariable=self.user,
                bg='white')

        labelsMap['Lot ID'] = tk.Label(
            self.parentFrame,
            font=FontTheme().primary,
            textvariable=self.lotId,
            bg='white')

        for labelText, entry in labelsMap.items():
            tk.Label(self.parentFrame, text=labelText, bg='white', font=FontTheme().primary).grid(row=row, column=0, sticky='w', padx=10)
            entry.grid(row=row, column=1, sticky="ew")
            row += 1
            ttk.Separator(self.parentFrame, orient="horizontal").grid(row=row, column=1, sticky="ew")
            row += 1
        row += 1
        return row

    def setConstants(self, lotId: str, user: str):
        self.lotId.set(lotId)
        self.user.set(user)
        self.parentFrame.grid()

    def setSaturation(self, saturationTime: str):
        self.saturationTime.set(saturationTime)

    def setSgi(self, sgi: float):
        self.sgi.set(f"{round(sgi, 1)}")

    def resetForm(self):
        self.lotId.set("")
        self.user.set("")
        self.sgi.set("-")
        self.saturationTime.set("No Estimate")

