import platform
import socket
import tkinter as tk
from tkinter import ttk

from src.app.common_modules.authentication.helpers.configuration import AuthConfiguration
from src.app.common_modules.authentication.helpers.logging import logAuthAction
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, createDropdown, styleDropdownOption, launchKeyboard, \
    formatPopup
from src.app.helper_methods.warehouse_configuration import WarehouseConfiguration
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.use_case.use_case_factory import ContextFactory
from src.app.widget.sidebar.helpers.functions import setHostname


class SystemConfigurationPage:
    def __init__(self, rootManager: RootManager, authorizer: str):
        self.RootManager = rootManager
        self.authorizer = authorizer
        self.AuthConfiguration = AuthConfiguration()
        self.WarehouseConfiguration = WarehouseConfiguration()
        self.windowRoot = rootManager.createTopLevel()
        self.includeWarehouse: bool = ContextFactory().getSetupFormConfig().includeWarehouse
        formatPopup(self.windowRoot)
        self.authEnabled = tk.StringVar(value=styleDropdownOption(self.AuthConfiguration.getConfig()))
        self.warehouse = tk.StringVar(value=self.WarehouseConfiguration.getConfig())
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.warningLabel = self.createCfrWarning()
        self.deviceId = tk.StringVar(value=socket.gethostname())
        self.authEnabled.trace_add("write", self.toggleWarning)
        self.authDropdown = self.createAuthDropdown(3)

        currentRow = 5
        if self.includeWarehouse:
            self.warehouseEntry = self.createWarehouse(currentRow)
            self.warehouseEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Warehouse:  "))
            currentRow += 1

        self.deviceIdEntry = self.createDeviceId(currentRow)
        self.deviceIdEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Device ID:  "))
        self.submitButton = self.createSubmitButton(currentRow + 1)
        self.cancelButton = self.createCancelButton(currentRow + 1)

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="System Configuration",
            font=FontTheme().header1,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createAuthDropdown(self, row: int):
        ttk.Label(
            self.windowRoot,
            text="Authentication Enabled: ",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=row, column=0)

        options = ["True", "False"]
        dropdown = createDropdown(self.windowRoot, self.authEnabled, options, outline=True)
        dropdown.grid(row=row, column=1, padx=10, pady=WidgetTheme().externalPadding, ipady=WidgetTheme().internalPadding, sticky="ew")
        return dropdown

    def createCfrWarning(self) -> ttk.Label:
        return ttk.Label(
            self.windowRoot,
            text="* Warning: Disabling user authentication will result in a system that is not CFR compliant.",
            font=FontTheme().warning,
            foreground=Colors().status.error,
            background=Colors().body.background)

    def toggleWarning(self, *args):
        if self.authEnabled.get().strip() == "False" and self.AuthConfiguration.getConfig():
            self.warningLabel.grid(row=4, column=0, columnspan=3, sticky="w")
        else:
            self.warningLabel.grid_forget()

    def createWarehouse(self, row: int):
        ttk.Label(
            self.windowRoot,
            text="Default Warehouse:",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=row, column=0, sticky="w")

        warehouseEntry = ttk.Entry(self.windowRoot, background="white", justify="center", textvariable=self.warehouse, font=FontTheme().primary)
        warehouseEntry.grid(row=row, column=1, padx=10, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding, sticky="ew")
        return warehouseEntry

    def createDeviceId(self, row: int):
        ttk.Label(
            self.windowRoot,
            text="Device ID:",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=row, column=0, sticky="w")

        deviceIdEntry = ttk.Entry(self.windowRoot, background="white", justify="center", textvariable=self.deviceId, font=FontTheme().primary)
        deviceIdEntry.grid(row=row, column=1, padx=10, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding, sticky="ew")
        return deviceIdEntry

    def createSubmitButton(self, row: int):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitConfig).button
        submitButton.grid(row=row, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        return submitButton

    def submitConfig(self):
        newAuthSetting = self.authEnabled.get().strip() == "True"
        if self.AuthConfiguration.getConfig() != newAuthSetting:
            self.submitAuthChanges(self.AuthConfiguration.getConfig(), newAuthSetting)
        if self.includeWarehouse:
            if self.WarehouseConfiguration.getConfig() != self.warehouse.get():
                self.submitWarehouseChanges(self.WarehouseConfiguration.getConfig(), self.warehouse.get())
        if self.deviceId.get() != socket.gethostname():
            self.updateHostname(socket.gethostname(), self.deviceId.get())
        self.windowRoot.destroy()

    def submitAuthChanges(self, oldSetting: bool, newSetting: bool):
        if platform.system() == "Linux":
            self.AuthConfiguration.setConfig(newSetting)
        else:
            self.AuthConfiguration.authenticationEnabled = newSetting
        logAuthAction(
            "Authentication Enabled",
            "Changed",
            self.authorizer,
            result=f"`{oldSetting}` to `{newSetting}`"
        )

    def submitWarehouseChanges(self, oldSetting: str, newSetting: str):
        if platform.system() == "Linux":
            self.WarehouseConfiguration.setConfig(newSetting)
        else:
            self.WarehouseConfiguration.warehouse = newSetting
        logAuthAction(
            "Default Warehouse",
            "Changed",
            self.authorizer,
            result=f"`{oldSetting}` to `{newSetting}`"
        )

    def updateHostname(self, oldSetting: str, newSetting: str):
        if platform.system() == "Linux":
            successful = setHostname(newSetting)
            if successful:
                logAuthAction(
                    "Hostname",
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
