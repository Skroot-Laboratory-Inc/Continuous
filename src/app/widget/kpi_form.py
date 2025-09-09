import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.configuration import AuthConfiguration
from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.reader.pump.pump_controller import PumpController
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.sidebar.helpers.run_exporter import RunExporter


class KpiForm:
    def __init__(self, parent: tk.Frame, rootManager: RootManager, sessionManager: SessionManager):
        """ Displays all relevant information for a scan to the user by placing them on the provided frame. """
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.sgi = tk.StringVar(value="-")
        self.runId = tk.StringVar()
        self.saturationTime = tk.StringVar(value="No Estimate")
        self.user = tk.StringVar()

        self.parentFrame = parent
        self.parentFrame.grid_rowconfigure(1, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(3, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(5, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(7, weight=1, minsize=50)
        self.PumpController = PumpController(self.parentFrame)
        row = self.addLabels(0)

    def addLabels(self, row):
        labelsMap = {}

        # labelsMap["Saturation"] = tk.Label(
        #     self.parentFrame,
        #     font=FontTheme().primary,
        #     textvariable=self.saturationTime,
        #     bg='white')

        labelsMap['Current SGI'] = tk.Label(
            self.parentFrame,
            font=FontTheme().primary,
            textvariable=self.sgi,
            bg='white')

        labelsMap['Run ID'] = tk.Label(
            self.parentFrame,
            font=FontTheme().primary,
            textvariable=self.runId,
            bg='white')

        if self.user != "":
            labelsMap['Started By'] = tk.Label(
                self.parentFrame,
                font=FontTheme().primary,
                textvariable=self.user,
                bg='white')

        for labelText, entry in labelsMap.items():
            tk.Label(self.parentFrame, text=labelText, bg='white', font=FontTheme().primary).grid(row=row, column=0, sticky='nsw', padx=10)
            entry.grid(row=row, column=1, sticky="nsew")
            row += 1
            ttk.Separator(self.parentFrame, orient="horizontal").grid(row=row, column=1, sticky="ew")
            row += 1

        self.PumpController.getToggle().grid(row=row, column=1, sticky="nsew")
        row += 1

        button = GenericButton(
            "Export Run",
            self.parentFrame,
            self.export
        ).button
        button.grid(row=row, column=0, sticky="w")
        row += 1
        return row

    def export(self):
        if AuthConfiguration().getConfig():
            RunExporter(
                self.rootManager,
                exportedBy=self.sessionManager.user.username,
                runId=self.runId.get(),
            )
        else:
            RunExporter(
                self.rootManager,
                runId=self.runId.get(),
            )

    def setConstants(self, lotId: str, user: str, pumpFlowRate: float):
        self.runId.set(lotId)
        self.user.set(user)
        self.PumpController.setFlowRate(pumpFlowRate)
        self.parentFrame.grid()

    def setSaturation(self, saturationTime: str):
        self.saturationTime.set(saturationTime)

    def setSgi(self, sgi: float):
        self.sgi.set(f"{round(sgi, 1)}")

    def resetForm(self):
        self.runId.set("")
        self.user.set("")
        self.sgi.set("-")
        self.saturationTime.set("No Estimate")


