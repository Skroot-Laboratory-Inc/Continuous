import logging
import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.exceptions import ConfigurationException, InvalidConfiguration
from src.app.authentication.password_policy_manager.dev_password_policy_manager import DevPasswordPolicyManager
from src.app.authentication.password_policy_manager.password_policy_manager import PasswordPolicyManager
from src.app.buttons.generic_button import GenericButton
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard
from src.app.properties.dev_properties import DevProperties
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification


class PasswordRequirementsScreen:
    def __init__(self, rootManager: RootManager):
        self.RootManager = rootManager
        try:
            if not DevProperties().isDevMode:
                self.PasswordPolicyManager: PasswordPolicyManager = PasswordPolicyManager()
            else:
                self.PasswordPolicyManager: PasswordPolicyManager = DevPasswordPolicyManager()
        except ConfigurationException as e:
            text_notification.setText(f"Failed to set configuration:\n{e.message}")
            logging.exception("Failed to instantiate PasswordPolicyManager", extra={"id": "Password Configuration"})
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.maxPasswordAge = tk.StringVar(value=str(self.PasswordPolicyManager.max_days))
        self.minPasswordAge = tk.StringVar(value=str(self.PasswordPolicyManager.min_days))
        self.inactiveDays = tk.StringVar(value=str(self.PasswordPolicyManager.inactive_days))
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.maxAgeEntry = self.createMaxPasswordAge()
        self.inactiveDaysEntry = self.createInactiveDays()
        self.submitButton = self.createSubmitButton()
        self.cancelButton = self.createCancelButton()

        self.maxAgeEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot()))
        self.inactiveDaysEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot()))

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Password Configurations",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)

    def createMaxPasswordAge(self):
        ttk.Label(
            self.windowRoot,
            text="Password Expiration (Days)",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=4, column=0)

        entry = tk.Entry(
            self.windowRoot,
            validate='all',
            validatecommand=self.RootManager.validateInteger,
            invalidcommand=self.RootManager.validateIntegerError,
            textvariable=self.maxPasswordAge,
        )
        entry.grid(row=4, column=1, padx=10, pady=10)
        return entry

    def createInactiveDays(self):
        ttk.Label(
            self.windowRoot,
            text="Inactive Lock Out (Days): ",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=6, column=0)

        entry = tk.Entry(
            self.windowRoot,
            validate='all',
            validatecommand=self.RootManager.validateInteger,
            invalidcommand=self.RootManager.validateIntegerError,
            textvariable=self.inactiveDays,
        )
        entry.grid(row=6, column=1, padx=10, pady=10)
        return entry

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitConfig).button
        submitButton.grid(row=7, column=1, pady=10, columnspan=2, sticky="e")
        return submitButton

    def submitConfig(self):
        if platform.system() == "Linux":
            try:
                self.PasswordPolicyManager.update_policy(
                    max_days=int(self.maxPasswordAge.get()),
                    inactive_days=int(self.inactiveDays.get()),
                )
                self.windowRoot.destroy()
                text_notification.setText("Configuration Updated.")
            except InvalidConfiguration as e:
                text_notification.setText(f"Invalid configuration:\n{e.message}")
                logging.info(f"Invalid configuration values:\n{e.message}", extra={"id": "Password Configuration"})
            except ConfigurationException as e:
                text_notification.setText(f"Failed to set configuration:\n{e.message}")
                logging.info(f"Failed to set configuration:\n{e.message}", extra={"id": "Password Configuration"})

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=7, column=0, pady=10, sticky="w")
        return cancelButton

    def cancel(self):
        self.windowRoot.destroy()
