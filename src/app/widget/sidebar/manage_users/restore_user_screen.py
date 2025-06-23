import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.exceptions import RetireUserException, \
    UserDoesntExistException, RestoreUserException
from src.app.authentication.helpers.functions import retireUser, restoreUser
from src.app.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.widget import text_notification
from src.app.widget.confirmation_popup import ConfirmationPopup


class RestoreUserScreen:
    def __init__(self, rootManager: RootManager, systemAdminUser: str):
        self.systemAdminUser = systemAdminUser
        self.RootManager = rootManager
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.username = tk.StringVar()
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.createUsernameEntry = self.createUsername()
        self.createUsernameEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot()))
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
            text="Restore a User",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)

    def createUsername(self):
        ttk.Label(
            self.windowRoot,
            text="Username",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=3, column=0)

        usernameEntry = ttk.Entry(self.windowRoot, width=25, background="white", justify="center",
                                  textvariable=self.username, font=FontTheme().primary)
        usernameEntry.grid(row=3, column=1, padx=10)
        return usernameEntry

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitRetireUser).button
        submitButton.grid(row=6, column=1, pady=10, columnspan=2, sticky="e")
        return submitButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancelReset).button
        cancelButton.grid(row=6, column=0, pady=10, sticky="w")
        return cancelButton

    def submitRetireUser(self):
        try:
            self.restoreUser()
            self.windowRoot.destroy()
        except UserConfirmationException as e:
            pass
        except RestoreUserException as e:
            text_notification.setText(f"Failed to restore user. \n{e.message}")
        except UserDoesntExistException:
            text_notification.setText(f"Failed to restore user.\n`{self.username.get()}` does not exist.")

    def restoreUser(self):
        ConfirmationPopup(
            self.RootManager,
            "Restore a Retired User",
            f"Are you sure you would like to restore user: {self.username.get()}?"
            f"\nThey will regain permissions previously allowed.",
        )
        success, message = restoreUser(self.systemAdminUser, self.username.get())
        if success:
            text_notification.setText(f"User '{self.username.get()}' restoration was successful.")
        else:
            raise RestoreUserException(message)

    def cancelReset(self):
        self.windowRoot.destroy()
