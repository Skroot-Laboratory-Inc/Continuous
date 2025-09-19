import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.logging import logAuthAction
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.sidebar.configurations.pump_configuration import PumpConfiguration


class PumpConfigurationPage:
    def __init__(self, rootManager: RootManager, user: str):
        self.RootManager = rootManager
        self.user = user
        self.PumpConfiguration = PumpConfiguration()
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(
            relief="solid", highlightbackground="black", highlightcolor="black", highlightthickness=1, bd=0,
        )
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.pumpFlowRate = tk.StringVar(value=self.PumpConfiguration.getConfig())
        self.pumpFlowRateEntry = self.createPumpFlowRate(2)
        self.submitButton = self.createSubmitButton(3)
        self.cancelButton = self.createCancelButton(3)
        self.pumpFlowRateEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Pump Flow Rate:  "))

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Pump Configuration",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createPumpFlowRate(self, row: int):
        ttk.Label(
            self.windowRoot,
            text="Default Flow Rate (mL/hour):",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=row, column=0, sticky="w")

        pumpFlowRateEntry = ttk.Entry(self.windowRoot, background="white", justify="center", textvariable=self.pumpFlowRate, font=FontTheme().primary)
        pumpFlowRateEntry.grid(row=row, column=1, padx=10, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding, sticky="ew")
        return pumpFlowRateEntry

    def createSubmitButton(self, row: int):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitConfig).button
        submitButton.grid(row=row, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        return submitButton

    def submitConfig(self):
        if self.pumpFlowRate.get() != self.PumpConfiguration.getConfig():
            self.updateFlowRate(self.PumpConfiguration.getConfig(), float(self.pumpFlowRate.get()))
        self.windowRoot.destroy()

    def updateFlowRate(self, oldSetting: float, newSetting: float):
        if platform.system() == "Linux":
            successful = self.PumpConfiguration.setConfig(newSetting)
            if successful:
                logAuthAction(
                    "Default Pump Flow Rate",
                    "Changed",
                    self.user,
                    result=f"`{oldSetting}` to `{newSetting}`"
                )

    def createCancelButton(self, row: int):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=row, column=0, pady=WidgetTheme().externalPadding, sticky="w")
        return cancelButton

    def cancel(self):
        self.windowRoot.destroy()
