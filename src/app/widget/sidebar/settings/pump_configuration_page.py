import platform
import tkinter as tk
from tkinter import ttk

from src.app.common_modules.authentication.helpers.logging import logAuthAction
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard, formatPopup
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification
from src.app.widget.sidebar.configurations.pump_configuration import PumpConfiguration
from src.app.widget.sidebar.configurations.pump_priming_configuration import PumpPrimingConfiguration


class PumpConfigurationPage:
    def __init__(self, rootManager: RootManager, user: str):
        self.RootManager = rootManager
        self.user = user
        self.PumpConfiguration = PumpConfiguration()
        self.PumpPrimingConfiguration = PumpPrimingConfiguration()
        self.windowRoot = rootManager.createTopLevel()
        self.validateRPM = (self.windowRoot.register(validateRPM), '%P')
        self.validateRPMError = (self.windowRoot.register(showValidationError))
        formatPopup(self.windowRoot)
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.pumpFlowRate = tk.StringVar(value=self.PumpConfiguration.getConfig())
        self.primingFlowRate = tk.StringVar(value=self.PumpPrimingConfiguration.getConfig())
        self.pumpFlowRateEntry = self.createPumpFlowRate(2)
        self.primingFlowRateEntry = self.createPrimingFlowRate(3)
        self.submitButton = self.createSubmitButton(4)
        self.cancelButton = self.createCancelButton(4)
        self.pumpFlowRate.trace('w', self.checkFields)
        self.primingFlowRate.trace('w', self.checkFields)
        self.checkFields()
        self.pumpFlowRateEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Pump RPM:  "))
        self.primingFlowRateEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Priming RPM:  "))

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
            background=Colors().body.background, foreground=Colors().body.text).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createPumpFlowRate(self, row: int):
        ttk.Label(
            self.windowRoot,
            text="Default Pump Speed (RPM):",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=row, column=0, sticky="w")

        pumpFlowRateEntry = ttk.Entry(
            self.windowRoot,
            background=Colors().body.background,
            justify="center",
            textvariable=self.pumpFlowRate,
            font=FontTheme().primary,
            validate='all',
            validatecommand=self.validateRPM,
            invalidcommand=self.validateRPMError,
        )
        pumpFlowRateEntry.grid(row=row, column=1, padx=10, ipady=WidgetTheme().internalPadding,
                               pady=WidgetTheme().externalPadding, sticky="ew")
        return pumpFlowRateEntry

    def createPrimingFlowRate(self, row: int):
        ttk.Label(
            self.windowRoot,
            text="Default Priming Speed (RPM):",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=row, column=0, sticky="w")

        pumpFlowRateEntry = ttk.Entry(
            self.windowRoot,
            background=Colors().body.background,
            justify="center",
            textvariable=self.primingFlowRate,
            font=FontTheme().primary,
            validate='all',
            validatecommand=self.validateRPM,
            invalidcommand=self.validateRPMError,
        )
        pumpFlowRateEntry.grid(row=row, column=1, padx=10, ipady=WidgetTheme().internalPadding,
                               pady=WidgetTheme().externalPadding, sticky="ew")
        return pumpFlowRateEntry

    def createSubmitButton(self, row: int):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitConfig).button
        submitButton.grid(row=row, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        return submitButton

    def submitConfig(self):
        if self.pumpFlowRate.get() != self.PumpConfiguration.getConfig():
            self.updateFlowRate(self.PumpConfiguration.getConfig(), float(self.pumpFlowRate.get()))
        if self.primingFlowRateEntry.get() != self.PumpPrimingConfiguration.getConfig():
            self.updatePrimingFlowRate(self.PumpPrimingConfiguration.getConfig(), float(self.primingFlowRateEntry.get()))
        self.windowRoot.destroy()

    def updateFlowRate(self, oldSetting: float, newSetting: float):
        if platform.system() == "Linux":
            self.PumpConfiguration.setConfig(newSetting)
            logAuthAction(
                "Default Pump Flow Rate",
                "Changed",
                self.user,
                result=f"`{oldSetting}` to `{newSetting}`"
            )

    def updatePrimingFlowRate(self, oldSetting: float, newSetting: float):
        if platform.system() == "Linux":
            self.PumpPrimingConfiguration.setConfig(newSetting)
            logAuthAction(
                "Default Priming Flow Rate",
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

    def checkFields(self, *args):
        """Enable submit button only if both fields have values"""
        if self.pumpFlowRate.get() and self.primingFlowRate.get():
            self.submitButton.config(state='normal')
        else:
            self.submitButton.config(state='disabled')


def validateRPM(P):
    if P == "":
        return True
    if 0.1 < float(P) < 600:
        return True
    else:
        return False


def showValidationError():
    text_notification.setText("Pump speeds cannot be less than 0.1 or greater than 600 RPM.")
