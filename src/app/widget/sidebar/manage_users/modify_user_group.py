import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.exceptions import UserDoesntExistException, SystemAdminException, \
    ModifyUserRoleException
from src.app.authentication.helpers.functions import getRole, modifyRole
from src.app.authentication.model.user_role import UserRole
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard, createDropdown, styleDropdownOption
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification


class ModifyUserGroup:
    def __init__(self, rootManager: RootManager, systemAdminUser: str):
        self.systemAdminUser = systemAdminUser
        self.RootManager = rootManager
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.username = tk.StringVar()
        self.group = tk.StringVar(value=styleDropdownOption("User"))
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.createGroupDropdown()
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
            text="Modify User Group",
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
        usernameEntry.grid(row=3, column=1, padx=10, pady=10, ipady=WidgetTheme().entryYPadding, sticky="ew")
        return usernameEntry

    def createGroupDropdown(self):
        ttk.Label(
            self.windowRoot,
            text="User Group",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=4, column=0)

        options = ["User", "Administrator"]
        dropdown = createDropdown(self.windowRoot, self.group, options, outline=True)
        dropdown.grid(row=4, column=1, padx=10, ipady=WidgetTheme().entryYPadding, sticky="ew")
        return dropdown

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitModifyUserGroup).button
        submitButton.grid(row=6, column=1, pady=10, columnspan=2, sticky="e")
        return submitButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancelModification).button
        cancelButton.grid(row=6, column=0, pady=10, sticky="w")
        return cancelButton

    def submitModifyUserGroup(self):
        try:
            currentRole = getRole(self.username.get())
            newRole = UserRole.ADMIN if self.group.get().strip() == "Administrator" else UserRole.USER
            if currentRole == UserRole.SYSTEM_ADMIN:
                raise SystemAdminException("Cannot change the role of the system administrator.")
            if currentRole == newRole:
                text_notification.setText(f"`{self.username.get()}` is already {newRole.prefixed_display_name}")
            else:
                modifyRole(self.systemAdminUser, self.username.get(), newRole)
                text_notification.setText(f"'{self.username.get()}' is now {newRole.prefixed_display_name}.")
                self.windowRoot.destroy()
        except SystemAdminException as e:
            text_notification.setText(f"Failed to modify role. \n{e.message}")
        except UserDoesntExistException:
            text_notification.setText(f"Failed to modify role.\n`{self.username.get()}` does not exist.")
        except ModifyUserRoleException as e:
            text_notification.setText(f"Failed to modify role. \n{e.message}")
        except Exception as e:
            text_notification.setText(f"Failed to modify role. \n{e}")

    def cancelModification(self):
        self.windowRoot.destroy()
