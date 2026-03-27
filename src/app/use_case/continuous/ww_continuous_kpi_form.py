import tkinter as tk
from tkinter import ttk

from src.app.common_modules.authentication.helpers.configuration import AuthConfiguration
from src.app.common_modules.authentication.helpers.decorators import requireUser
from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.widget.kpi_form.kpi_form_base import KpiForm
from src.app.widget.sidebar.helpers.run_exporter import RunExporter


class WWContinuousKpiForm(KpiForm):
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

        labelsMap['Harvest'] = tk.Label(
            self.parentFrame,
            font=FontTheme().primary,
            textvariable=self._harvestRecommendation,
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

        button = GenericButton(
            "Export Run",
            self.parentFrame,
            self.export
        ).button
        button.grid(row=row, column=0, sticky="w")
        row += 1
        return row

    def submitSecondaryAxisData(self, data: str):
        pass

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
        self.parentFrame.grid()

    def resetForm(self):
        self._runId.set("")
        self._user.set("")
        self._sgi.set("-")
        self._saturationTime.set("")
        self._saturationDate = None
        self._harvestRecommendation.set("")
        self.parentFrame.grid_remove()
