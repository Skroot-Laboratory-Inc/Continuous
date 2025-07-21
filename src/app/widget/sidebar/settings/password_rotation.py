import logging
import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.exceptions import ConfigurationException, InvalidConfiguration
from src.app.authentication.helpers.logging import logAuthAction
from src.app.authentication.password_policy_manager.dev_password_rotation_manager import DevPasswordRotationManager
from src.app.authentication.password_policy_manager.password_rotation_manager import PasswordRotationManager
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification


class PasswordRotationScreen:
    def __init__(self, rootManager: RootManager, authorizer: str):
        self.RootManager = rootManager
        self.authorizer = authorizer
        try:
            if platform.system() == "Linux":
                self.PasswordPolicyManager: PasswordRotationManager = PasswordRotationManager()
            else:
                self.PasswordPolicyManager: PasswordRotationManager = DevPasswordRotationManager()
        except ConfigurationException as e:
            text_notification.setText(f"Failed to set configuration:\n{e.message}")
            logging.exception("Failed to instantiate PasswordPolicyManager", extra={"id": "Password Configuration"})
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.maxPasswordAge = tk.StringVar(value=str(self.PasswordPolicyManager.max_days))
        self.historicPasswords = tk.StringVar(value=str(self.PasswordPolicyManager.historic_passwords))
        self.inactiveDays = tk.StringVar(value=str(self.PasswordPolicyManager.inactive_days))
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.maxAgeEntry = self.createMaxPasswordAge(row=2)
        self.inactiveDaysEntry = self.createInactiveDays(row=3)
        self.historicPasswordsEntry = self.createHistoricPasswords(row=4)
        self.submitButton = self.createSubmitButton(row=5)
        self.cancelButton = self.createCancelButton(row=5)

        self.maxAgeEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Password Age:  "))
        self.inactiveDaysEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Inactive Days:  "))
        self.historicPasswordsEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Remembered Passwords:  "))

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Password Rotation",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createMaxPasswordAge(self, row: int):
        frame = tk.Frame(self.windowRoot, bg=Colors().secondaryColor)
        frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=WidgetTheme().externalPadding)

        ttk.Label(
            frame,
            text="Password expires ",
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
            textvariable=self.maxPasswordAge,
            width=8
        )
        entry.grid(row=0, column=1, padx=(0, 5), ipady=WidgetTheme().internalPadding)

        ttk.Label(
            frame,
            text=" days after creation.",
            font=FontTheme().primary,
            background=Colors().secondaryColor
        ).grid(row=0, column=2, sticky='w')

        return entry

    def createInactiveDays(self, row: int):
        frame = tk.Frame(self.windowRoot, bg=Colors().secondaryColor)
        frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=WidgetTheme().externalPadding)

        ttk.Label(
            frame,
            text="User is locked out ",
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
            textvariable=self.inactiveDays,
            width=8
        )
        entry.grid(row=0, column=1, padx=(0, 5), ipady=WidgetTheme().internalPadding)

        ttk.Label(
            frame,
            text=" days after expiration.",
            font=FontTheme().primary,
            background=Colors().secondaryColor
        ).grid(row=0, column=2, sticky='w')

        return entry

    def createHistoricPasswords(self, row: int):
        frame = tk.Frame(self.windowRoot, bg=Colors().secondaryColor)
        frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=WidgetTheme().externalPadding)

        ttk.Label(
            frame,
            text="User cannot re-use last ",
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
            textvariable=self.historicPasswords,
            width=8
        )
        entry.grid(row=0, column=1, padx=(0, 5), ipady=WidgetTheme().internalPadding)

        ttk.Label(
            frame,
            text=" password(s).",
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
            if self.PasswordPolicyManager.max_days != int(self.maxPasswordAge.get()):
                logAuthAction(
                    "Max Password Age",
                    "Changed",
                    self.authorizer,
                    result=f"`{self.PasswordPolicyManager.max_days}` to `{int(self.maxPasswordAge.get())}`"
                )
            if self.PasswordPolicyManager.inactive_days != int(self.inactiveDays.get()):
                logAuthAction(
                    "Inactive Lock Out Days",
                    "Changed",
                    self.authorizer,
                    result=f"`{self.PasswordPolicyManager.inactive_days}` to `{int(self.inactiveDays.get())}`"
                )
            if self.PasswordPolicyManager.historic_passwords != int(self.historicPasswords.get()):
                logAuthAction(
                    "Historic Passwords",
                    "Changed",
                    self.authorizer,
                    result=f"`{self.PasswordPolicyManager.historic_passwords}` to `{int(self.historicPasswords.get())}`"
                )
            try:
                self.PasswordPolicyManager.update_policy(
                    max_days=int(self.maxPasswordAge.get()),
                    inactive_days=int(self.inactiveDays.get()),
                    historic_passwords=int(self.historicPasswords.get()),
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
