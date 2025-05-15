import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.configuration import AuthConfiguration
from src.app.buttons.generic_button import GenericButton
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, createDropdown, styleDropdownOption
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager


class SystemConfigurationPage:
    def __init__(self, rootManager: RootManager):
        self.RootManager = rootManager
        self.AuthConfiguration = AuthConfiguration()
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.authEnabled = tk.StringVar(value=styleDropdownOption(self.AuthConfiguration.authenticationEnabled))
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.warningLabel = self.createCfrWarning()
        self.authEnabled.trace_add("write", self.toggleWarning)
        self.authDropdown = self.createAuthDropdown()
        self.submitButton = self.createSubmitButton()
        self.cancelButton = self.createCancelButton()

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Configurations",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)

    def createAuthDropdown(self):
        ttk.Label(
            self.windowRoot,
            text="Authentication Enabled",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=3, column=0)

        options = ["True", "False"]
        dropdown = createDropdown(self.windowRoot, self.authEnabled, options, addSpace=True)
        dropdown.grid(row=3, column=1, padx=10, pady=10)
        return dropdown

    def createCfrWarning(self) -> ttk.Label:
        return ttk.Label(
            self.windowRoot,
            text="* Warning: Disabling user authentication will result in a system that is not CFR compliant.",
            font=FontTheme().warning,
            foreground=Colors().lightRed,
            background=Colors().secondaryColor)

    def toggleWarning(self, *args):
        if self.authEnabled.get().strip() == "False" and self.AuthConfiguration.authenticationEnabled:
            self.warningLabel.grid(row=4, column=0, columnspan=3, sticky="w")
        else:
            self.warningLabel.grid_forget()

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitConfig).button
        submitButton.grid(row=6, column=1, pady=10, columnspan=2, sticky="e")
        return submitButton

    def submitConfig(self):
        if platform.system() == "Linux":
            self.AuthConfiguration.setAuthConfiguration(self.authEnabled.get().strip() == "True")
        else:
            self.AuthConfiguration.authenticationEnabled = self.authEnabled.get().strip() == "True"
        self.windowRoot.destroy()

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=6, column=0, pady=10, sticky="w")
        return cancelButton

    def cancel(self):
        self.windowRoot.destroy()
