import tkinter as tk
from tkinter import ttk

from reactivex import Subject

from src.app.authentication.helpers.configuration import AuthConfiguration
from src.app.authentication.helpers.decorators import requireUser
from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.helper_methods.ui_helpers import launchKeyboard
from src.app.reader.pump.pump_controller import PumpController
from src.app.reader.pump.pump_interface import PumpInterface
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.buttons.submit_arrow_button import SubmitArrowButton
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.sidebar.configurations.secondary_axis_type import SecondaryAxisType
from src.app.widget.sidebar.configurations.secondary_axis_units import SecondaryAxisUnits
from src.app.widget.sidebar.helpers.run_exporter import RunExporter


class KpiForm:
    def __init__(self, parent: tk.Frame, rootManager: RootManager, sessionManager: SessionManager, pump: PumpInterface):
        """ Displays all relevant information for a scan to the user by placing them on the provided frame. """
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.sgi = tk.StringVar(value="-")
        self.runId = tk.StringVar()
        self.saturationTime = tk.StringVar(value="No Estimate")
        self.user = tk.StringVar()
        self.axisLabel = tk.StringVar(value=f"{SecondaryAxisType().getConfig()} ({SecondaryAxisUnits().getConfig()}):")
        self.secondaryAxisData = tk.StringVar(value="")
        self.lastSecondAxisEntry = Subject()

        self.parentFrame = parent
        self.parentFrame.grid_rowconfigure(1, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(3, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(5, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(7, weight=1, minsize=50)
        self.PumpController = PumpController(self.parentFrame, pump)
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
        row = self.createSecondaryAxisRow(row)

        self.PumpController.getToggle().grid(row=row, column=1, sticky="nse")

        button = GenericButton(
            "Export Run",
            self.parentFrame,
            self.export
        ).button
        button.grid(row=row, column=0, sticky="w")
        row += 1
        return row

    def createSecondaryAxisRow(self, row):
        secondaryAxisFrame = tk.Frame(self.parentFrame, bg='white')
        secondaryAxisFrame.grid(row=row, column=0, columnspan=2, sticky="nsew")
        secondaryAxisFrame.grid_columnconfigure(1, weight=1)

        tk.Label(
            secondaryAxisFrame,
            textvariable=self.axisLabel,
            bg='white',
            font=FontTheme().primary).grid(row=row, column=0, sticky='e', padx=10)
        secondaryAxisEntry = ttk.Entry(
            secondaryAxisFrame,
            font=FontTheme().primary,
            width=5,
            textvariable=self.secondaryAxisData,
            background='white')
        secondaryAxisEntry.grid(row=row, column=1, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding, sticky="nsew")
        secondaryAxisEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, self.rootManager.getRoot(), f"{SecondaryAxisType().getConfig()}:  "))
        self.submitButton = SubmitArrowButton(
            secondaryAxisFrame,
            lambda: self.submitSecondaryAxisData(secondaryAxisEntry.get())
        ).button
        self.submitButton.grid(row=row, column=2, sticky="nsw", ipady=WidgetTheme().internalPadding, ipadx=WidgetTheme().internalPadding)
        self.secondaryAxisData.trace_add("write", self.validateSecondaryAxisInput)
        row += 1
        return row

    def validateSecondaryAxisInput(self, *args):
        try:
            float(self.secondaryAxisData.get())
            self.submitButton.config(state='normal')
        except ValueError:
            self.submitButton.config(state='disabled')

    def submitSecondaryAxisData(self, data: str):
        self.lastSecondAxisEntry.on_next(data)
        self.secondaryAxisData.set("")

    @requireUser
    def export(self):
        if AuthConfiguration().getConfig():
            RunExporter(
                self.rootManager,
                exportedBy=self.sessionManager.getUser(),
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
        self.axisLabel.set(f"{SecondaryAxisType().getConfig()} ({SecondaryAxisUnits().getConfig()}):")
        self.secondaryAxisData.set("")
        self.PumpController.setFlowRate(pumpFlowRate)
        self.PumpController.setPriming(False)
        self.parentFrame.grid()

    def setSaturation(self, saturationTime: str):
        self.saturationTime.set(saturationTime)

    def setSgi(self, sgi: float):
        self.sgi.set(f"{round(sgi, 1)}")

    def resetForm(self):
        self.runId.set("")
        self.user.set("")
        self.sgi.set("-")
        self.PumpController.stop()
        self.PumpController.setPriming(True)
        self.saturationTime.set("No Estimate")
        self.parentFrame.grid_remove()
