import tkinter as tk
from tkinter import ttk

from src.app.common_modules.authentication.helpers.configuration import AuthConfiguration
from src.app.common_modules.authentication.helpers.decorators import requireUser
from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.helper_methods.ui_helpers import launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.buttons.submit_arrow_button import SubmitArrowButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.kpi_form.kpi_form_base import KpiForm
from src.app.widget.sidebar.configurations.secondary_axis_type import SecondaryAxisType
from src.app.widget.sidebar.configurations.secondary_axis_units import SecondaryAxisUnits
from src.app.widget.sidebar.helpers.run_exporter import RunExporter


class TunairKpiForm(KpiForm):
    def __init__(self, parent: tk.Frame, rootManager: RootManager, sessionManager: SessionManager):
        """ Displays all relevant information for a scan to the user by placing them on the provided frame. """
        super().__init__()
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.parentFrame = parent
        self.parentFrame.grid_rowconfigure(1, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(3, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(5, weight=1, minsize=50)
        self.parentFrame.grid_rowconfigure(7, weight=1, minsize=50)
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
            bg=Colors().body.background,
            fg=Colors().body.text)

        labelsMap['Run ID'] = tk.Label(
            self.parentFrame,
            font=FontTheme().primary,
            textvariable=self._runId,
            bg=Colors().body.background,
            fg=Colors().body.text)

        if self._user != "":
            labelsMap['Started By'] = tk.Label(
                self.parentFrame,
                font=FontTheme().primary,
                textvariable=self._user,
                bg=Colors().body.background,
                fg=Colors().body.text)

        for labelText, entry in labelsMap.items():
            tk.Label(
                self.parentFrame,
                text=labelText,
                bg=Colors().body.background,
                fg=Colors().body.text,
                font=FontTheme().primary,
            ).grid(row=row, column=0, sticky='nsw', padx=10)
            entry.grid(row=row, column=1, sticky="nsew")
            row += 1
            ttk.Separator(self.parentFrame, orient="horizontal").grid(row=row, column=1, sticky="ew")
            row += 1
        row = self.createSecondaryAxisRow(row)

        button = GenericButton(
            "Export Run",
            self.parentFrame,
            self.export
        ).button
        button.grid(row=row, column=0, sticky="w")
        row += 1
        return row

    def createSecondaryAxisRow(self, row):
        secondaryAxisFrame = tk.Frame(self.parentFrame, bg=Colors().body.background)
        secondaryAxisFrame.grid(row=row, column=0, columnspan=2, sticky="nsew")
        secondaryAxisFrame.grid_columnconfigure(1, weight=1)

        tk.Label(
            secondaryAxisFrame,
            textvariable=self._axisLabel,
            bg=Colors().body.background,
            fg=Colors().body.text,
            font=FontTheme().primary).grid(row=row, column=0, sticky='e', padx=10)
        secondaryAxisEntry = ttk.Entry(
            secondaryAxisFrame,
            font=FontTheme().primary,
            width=5,
            textvariable=self._secondaryAxisData,
            background=Colors().body.background)
        secondaryAxisEntry.grid(row=row, column=1, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding, sticky="nsew")
        secondaryAxisEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, self.rootManager.getRoot(), f"{SecondaryAxisType().getConfig()}:  "))
        self.submitButton = SubmitArrowButton(
            secondaryAxisFrame,
            lambda: self.submitSecondaryAxisData(secondaryAxisEntry.get())
        ).button
        self.submitButton.grid(row=row, column=2, sticky="nsw", ipady=WidgetTheme().internalPadding, ipadx=WidgetTheme().internalPadding)
        self._secondaryAxisData.trace_add("write", self.validateSecondaryAxisInput)
        row += 1
        return row

    def validateSecondaryAxisInput(self, *args):
        try:
            float(self._secondaryAxisData.get())
            self.submitButton.config(state='normal')
        except ValueError:
            self.submitButton.config(state='disabled')

    def submitSecondaryAxisData(self, data: str):
        self._lastSecondAxisEntry.on_next(data)
        self._secondaryAxisData.set("")

    @requireUser
    def export(self):
        if AuthConfiguration().getConfig():
            RunExporter(
                self.rootManager,
                exportedBy=self.sessionManager.getUser(),
                runId=self._runId.get(),
            )
        else:
            RunExporter(
                self.rootManager,
                runId=self._runId.get(),
            )

    def setConstants(self, lotId: str, user: str):
        self._runId.set(lotId)
        self._user.set(user)
        self._axisLabel.set(f"{SecondaryAxisType().getConfig()} {SecondaryAxisUnits().getAsUnit()}:")
        self._secondaryAxisData.set("")
        self.parentFrame.grid()

    def resetForm(self):
        self._runId.set("")
        self._user.set("")
        self._sgi.set("-")
        self._saturationTime.set("")
        self._saturationDate = None
        self._saturationTime.set("")
        self.parentFrame.grid_remove()


