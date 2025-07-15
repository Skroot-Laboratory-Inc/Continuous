import logging
import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.exceptions import ConfigurationException, InvalidConfiguration
from src.app.authentication.helpers.logging import logAuthAction
from src.app.authentication.password_requirements_manager.dev_password_requirements_manager import \
    DevPasswordRequirementsManager
from src.app.authentication.password_requirements_manager.password_requirements_manager import \
    PasswordRequirementsManager
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification


class PasswordRequirementsScreen:
    def __init__(self, rootManager: RootManager, authorizer: str):
        self.RootManager = rootManager
        self.authorizer = authorizer
        try:
            if platform.system() == "Linux":
                self.PasswordRequirementsManager: PasswordRequirementsManager = PasswordRequirementsManager()
            else:
                self.PasswordRequirementsManager: PasswordRequirementsManager = DevPasswordRequirementsManager()
        except ConfigurationException as e:
            text_notification.setText(f"Failed to set configuration:\n{e.message}")
            logging.exception("Failed to instantiate PasswordPolicyManager", extra={"id": "Password Configuration"})
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.lockoutMinutes = tk.StringVar(value=str(self.PasswordRequirementsManager.lockout_minutes))
        self.lockoutRetries = tk.StringVar(value=str(self.PasswordRequirementsManager.lockout_retries))
        self.minPasswordLength = tk.StringVar(value=str(self.PasswordRequirementsManager.minimum_password_length))
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.minPasswordLengthEntry = self.createMinPasswordLength(row=2)
        self.lockoutRetriesEntry = self.createLockoutRetries(row=3)
        self.lockoutMinutesEntry = self.createLockoutMinutes(row=4)
        self.submitButton = self.createSubmitButton(row=5)
        self.cancelButton = self.createCancelButton(row=5)

        self.lockoutMinutesEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot()))
        self.lockoutRetriesEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot()))
        self.minPasswordLengthEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot()))

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Password Requirements",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createLockoutMinutes(self, row: int):
        frame = tk.Frame(self.windowRoot, bg=Colors().secondaryColor)
        frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=WidgetTheme().externalPadding)

        ttk.Label(
            frame,
            text="User is disabled for ",
            font=FontTheme().primary,
            background=Colors().secondaryColor
        ).grid(row=0, column=0, sticky='w')
        entry = tk.Entry(
            frame,
            font=FontTheme().primary,
            justify=tk.CENTER,
            validate='all',
            validatecommand=self.RootManager.validateInteger,
            invalidcommand=self.RootManager.validateIntegerError,
            textvariable=self.lockoutMinutes,
            width=8
        )
        entry.grid(row=0, column=1, padx=(0, 5), ipady=WidgetTheme().internalPadding)
        ttk.Label(
            frame,
            text=" minute(s) on lockout.",
            font=FontTheme().primary,
            background=Colors().secondaryColor
        ).grid(row=0, column=2, sticky='w')

        return entry

    def createLockoutRetries(self, row: int):
        frame = tk.Frame(self.windowRoot, bg=Colors().secondaryColor)
        frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=WidgetTheme().externalPadding)
        ttk.Label(
            frame,
            text="User is allowed ",
            font=FontTheme().primary,
            background=Colors().secondaryColor
        ).grid(row=0, column=0, sticky='w')

        entry = tk.Entry(
            frame,
            font=FontTheme().primary,
            justify=tk.CENTER,
            validate='all',
            validatecommand=self.RootManager.validateInteger,
            invalidcommand=self.RootManager.validateIntegerError,
            textvariable=self.lockoutRetries,
            width=8
        )
        entry.grid(row=0, column=1, padx=(0, 5), ipady=WidgetTheme().internalPadding)

        ttk.Label(
            frame,
            text=" attempt(s) before lockout.",
            font=FontTheme().primary,
            background=Colors().secondaryColor
        ).grid(row=0, column=2, sticky='w')

        return entry

    def createMinPasswordLength(self, row: int):
        frame = tk.Frame(self.windowRoot, bg=Colors().secondaryColor)
        frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=WidgetTheme().externalPadding)

        ttk.Label(
            frame,
            text="Minimum password length is ",
            font=FontTheme().primary,
            background=Colors().secondaryColor
        ).grid(row=0, column=0, sticky='w')

        entry = tk.Entry(
            frame,
            font=FontTheme().primary,
            justify=tk.CENTER,
            validate='all',
            validatecommand=self.RootManager.validateInteger,
            invalidcommand=self.RootManager.validateIntegerError,
            textvariable=self.minPasswordLength,
            width=8,
        )
        entry.grid(row=0, column=1, padx=(0, 5), ipady=WidgetTheme().internalPadding)

        ttk.Label(
            frame,
            text=" characters.",
            font=FontTheme().primary,
            background=Colors().secondaryColor
        ).grid(row=0, column=2, sticky='w')

        return entry

    def createSubmitButton(self, row: int):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitConfig).button
        submitButton.grid(row=row, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        return submitButton

    def submitConfig(self):
        if platform.system() == "Linux":
            if self.PasswordRequirementsManager.lockout_minutes != int(self.lockoutMinutes.get()):
                logAuthAction(
                    "Max Password Age",
                    "Changed",
                    self.authorizer,
                    result=f"`{self.PasswordRequirementsManager.lockout_minutes}` to `{int(self.lockoutMinutes.get())}`"
                )
            if self.PasswordRequirementsManager.lockout_retries != int(self.lockoutRetries.get()):
                logAuthAction(
                    "Inactive Lock Out Days",
                    "Changed",
                    self.authorizer,
                    result=f"`{self.PasswordRequirementsManager.lockout_retries}` to `{int(self.lockoutRetries.get())}`"
                )
            if self.PasswordRequirementsManager.minimum_password_length != int(self.minPasswordLength.get()):
                logAuthAction(
                    "Minimum Password Length",
                    "Changed",
                    self.authorizer,
                    result=f"`{self.PasswordRequirementsManager.minimum_password_length}` to `{int(self.minPasswordLength.get())}`"
                )
            try:
                self.PasswordRequirementsManager.update_requirements(
                    lockout_minutes=int(self.lockoutMinutes.get()),
                    lockout_retries=int(self.lockoutRetries.get()),
                    minimum_password_length=int(self.minPasswordLength.get()),
                )
                self.windowRoot.destroy()
                text_notification.setText("Configuration Updated.")
            except InvalidConfiguration as e:
                text_notification.setText(f"Invalid configuration:\n{e.message}")
                logging.info(f"Invalid configuration values:\n{e.message}", extra={"id": "Password Configuration"})
            except ConfigurationException as e:
                text_notification.setText(f"Failed to set configuration:\n{e.message}")
                logging.info(f"Failed to set configuration:\n{e.message}", extra={"id": "Password Configuration"})
        else:
            self.windowRoot.destroy()

    def createCancelButton(self, row: int):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=row, column=0, pady=WidgetTheme().externalPadding, sticky="w")
        return cancelButton

    def cancel(self):
        self.windowRoot.destroy()
