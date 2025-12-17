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
from src.app.widget.sidebar.configurations.secondary_axis_type import SecondaryAxisType
from src.app.widget.sidebar.configurations.secondary_axis_units import SecondaryAxisUnits


class SecondaryAxisPage:
    def __init__(self, rootManager: RootManager, authorizer: str):
        self.RootManager = rootManager
        self.authorizer = authorizer
        self.SecondaryAxisTypeConfig = SecondaryAxisType()
        self.SecondaryAxisUnitsConfig = SecondaryAxisUnits()
        self.windowRoot = rootManager.createTopLevel()
        formatPopup(self.windowRoot)
        self.axisUnits = tk.StringVar(value=self.SecondaryAxisUnitsConfig.getConfig())
        self.axisType = tk.StringVar(value=self.SecondaryAxisTypeConfig.getConfig())
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.axisTypeEntry = self.createAxisType(2)
        self.axisUnitsEntry = self.createAxisUnits(3)
        self.axisTypeEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Measurement:  "))
        self.axisUnitsEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Units:  "))
        self.submitButton = self.createSubmitButton(6)
        self.cancelButton = self.createCancelButton(6)

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Secondary Axis Configuration",
            font=FontTheme().header1,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createAxisType(self, row: int):
        ttk.Label(
            self.windowRoot,
            text="Measurement Type: ",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=row, column=0)

        axisTypeEntry = ttk.Entry(self.windowRoot, background="white", justify="center", textvariable=self.axisType, font=FontTheme().primary)
        axisTypeEntry.grid(row=row, column=1, padx=10, pady=WidgetTheme().externalPadding, ipady=WidgetTheme().internalPadding, sticky="ew")
        return axisTypeEntry

    def createAxisUnits(self, row: int):
        ttk.Label(
            self.windowRoot,
            text="Units:",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=row, column=0, sticky="w")

        deviceIdEntry = ttk.Entry(self.windowRoot, background="white", justify="center", textvariable=self.axisUnits, font=FontTheme().primary)
        deviceIdEntry.grid(row=row, column=1, padx=10, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding, sticky="ew")
        return deviceIdEntry

    def createSubmitButton(self, row: int):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitConfig).button
        submitButton.grid(row=row, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        return submitButton

    def submitConfig(self):
        if self.SecondaryAxisTypeConfig.getConfig() != self.axisType.get().strip():
            self.submitAxisTypeChanges(self.SecondaryAxisTypeConfig.getConfig(), self.axisType.get().strip())
        if self.SecondaryAxisUnitsConfig.getConfig() != self.axisUnits.get().strip():
            self.submitUnitChanges(self.SecondaryAxisUnitsConfig.getConfig(), self.axisUnits.get().strip())
        self.windowRoot.destroy()

    def submitUnitChanges(self, oldSetting: str, newSetting: str):
        if platform.system() == "Linux":
            self.SecondaryAxisUnitsConfig.setConfig(newSetting)
        else:
            self.SecondaryAxisUnitsConfig.secondaryAxisUnits = newSetting
        logAuthAction(
            "Secondary Axis Units",
            "Changed",
            self.authorizer,
            result=f"`{oldSetting}` to `{newSetting}`"
        )

    def submitAxisTypeChanges(self, oldSetting: str, newSetting: str):
        if platform.system() == "Linux":
            self.SecondaryAxisTypeConfig.setConfig(newSetting)
        else:
            self.SecondaryAxisTypeConfig.secondaryAxisType = newSetting
        logAuthAction(
            "Secondary Axis Type",
            "Changed",
            self.authorizer,
            result=f"`{oldSetting}` to `{newSetting}`"
        )

    def createCancelButton(self, row: int):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=row, column=0, pady=WidgetTheme().externalPadding, sticky="w")
        return cancelButton

    def cancel(self):
        self.windowRoot.destroy()
