import platform
import tkinter as tk
from tkinter import ttk

from src.app.common_modules.authentication.helpers.exceptions import UserDoesntExistException, InsufficientPermissions, \
    SystemAdminException, RetireUserException
from src.app.common_modules.authentication.helpers.functions import retireUser
from src.app.helper_methods.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard, formatPopup
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification
from src.app.widget.confirmation_popup import ConfirmationPopup


class RetireUserScreen:
    def __init__(self, rootManager: RootManager, systemAdminUser: str):
        self.systemAdminUser = systemAdminUser
        self.RootManager = rootManager
        self.windowRoot = rootManager.createTopLevel()
        formatPopup(self.windowRoot)
        self.username = tk.StringVar()
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.createWarning()
        self.createUsernameEntry = self.createUsername()
        self.createUsernameEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Username:  "))
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
            text="Retire a User",
            font=FontTheme().header1,
            background=Colors().body.background, foreground=Colors().body.text).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createUsername(self):
        ttk.Label(
            self.windowRoot,
            text="Username",
            font=FontTheme().primary,
            background=Colors().body.background, foreground=Colors().body.text).grid(row=3, column=0)

        usernameEntry = ttk.Entry(self.windowRoot, width=25, background="white", justify="center",
                                  textvariable=self.username, font=FontTheme().primary)
        usernameEntry.grid(row=3, column=1, padx=10, ipady=WidgetTheme().internalPadding)
        return usernameEntry

    def createWarning(self):
        ttk.Label(
            self.windowRoot,
            text="* Warning: Retiring a user will revoke all access to the system for that user.",
            font=FontTheme().warning,
            foreground=Colors().status.error,
            background=Colors().body.background).grid(row=4, column=0, columnspan=3, sticky="w")

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitRetireUser).button
        submitButton.grid(row=6, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        return submitButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancelReset).button
        cancelButton.grid(row=6, column=0, pady=WidgetTheme().externalPadding, sticky="w")
        return cancelButton

    def submitRetireUser(self):
        try:
            self.retireUser()
            text_notification.setText(f"System user '{self.username.get()}' has been retired.")
            self.windowRoot.destroy()
        except UserConfirmationException:
            pass
        except UserDoesntExistException:
            text_notification.setText(f"Failed to retire user.\n`{self.username.get()}` does not exist.")
        except SystemAdminException as e:
            text_notification.setText(f"Failed to retire user. \n{e.message}")
        except InsufficientPermissions as e:
            text_notification.setText(f"Failed to retire user. \n{e.message}")
        except RetireUserException as e:
            text_notification.setText(f"Failed to retire user. \n{e.message}")

    def retireUser(self):
        ConfirmationPopup(
            self.RootManager,
            "Retire User",
            f"Are you sure you would like to retire user: {self.username.get()}?"
            f"\n{self.username.get()} will not be able to access the system until restored.",
        )
        retireUser(self.systemAdminUser, self.username.get())

    def cancelReset(self):
        self.windowRoot.destroy()
