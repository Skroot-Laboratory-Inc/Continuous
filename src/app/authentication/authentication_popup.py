import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.configuration import AuthConfiguration
from src.app.authentication.helpers.exceptions import IncorrectPasswordException, NotAdministratorException, \
    NotSystemAdmin, PamException, PasswordExpired, UserDoesntExistException
from src.app.authentication.helpers.functions import validateUserCredentials, getLockedOutUsers, getRole
from src.app.authentication.lockout_notification import LockoutNotification
from src.app.authentication.model.user_role import UserRole
from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification
from src.app.widget.sidebar.manage_users.password_reset_screen import PasswordResetScreen


class AuthenticationPopup:
    def __init__(self, rootManager: RootManager, sessionManager: SessionManager = None,
                 administratorRequired: bool = False, systemAdminRequired: bool = False, forceAuthenticate: bool = False):
        if AuthConfiguration().getConfig() or forceAuthenticate:
            self.isAuthenticated = False
            self.administratorRequired = administratorRequired
            self.systemAdminRequired = systemAdminRequired
            self.RootManager = rootManager
            self.sessionManager = sessionManager
            self.windowRoot = rootManager.createTopLevel()
            self.windowRoot.config(relief="solid", highlightbackground="black",
                highlightcolor="black", highlightthickness=1, bd=0)
            self.username = tk.StringVar()
            self.password = tk.StringVar()
            self.windowRoot.transient(rootManager.getRoot())
            self.createHeader()
            self.createUsernameEntry = self.createUsername()
            self.createUsernameEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot()))
            self.createPasswordEntry, self.showPasswordButton = self.createPassword()
            self.createPasswordEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), True))
            self.submitButton = self.createSubmitButton()
            self.cancelButton = self.createCancelButton()
            centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
            if platform.system() == "Windows":
                self.windowRoot.overrideredirect(True)
                self.windowRoot.attributes('-topmost', True)
            rootManager.waitForWindow(self.windowRoot)
        else:
            self.isAuthenticated = True

    def getUser(self):
        if AuthConfiguration().getConfig():
            return self.username.get()
        else:
            return ""

    def createHeader(self):
        if self.administratorRequired:
            label = "Administrator Sign In"
        elif self.systemAdminRequired:
            label = "System Admin Sign In"
        else:
            label = "Sign In"
        ttk.Label(
            self.windowRoot,
            text=label,
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)

    def createUsername(self):
        ttk.Label(
            self.windowRoot,
            text="Username:",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=2, column=0)

        usernameEntry = ttk.Entry(self.windowRoot, width=25, background="white", textvariable=self.username, font=FontTheme().primary)
        usernameEntry['state'] = tk.DISABLED
        usernameEntry.grid(row=2, column=1, padx=10, ipady=WidgetTheme().entryYPadding, pady=10)
        return usernameEntry

    def createPassword(self):
        ttk.Label(
            self.windowRoot,
            text="Password:",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=3, column=0)

        passwordEntry = ttk.Entry(self.windowRoot, show="*", width=25, background="white", textvariable=self.password, font=FontTheme().primary)
        passwordEntry.grid(row=3, column=1, padx=10, ipady=WidgetTheme().entryYPadding)

        showPasswordButton = ttk.Button(self.windowRoot, text="Show", command=self.togglePassword, style='Entry.TButton')
        showPasswordButton.grid(row=3, column=2)
        return passwordEntry, showPasswordButton

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitAuthentication).button
        submitButton.grid(row=4, column=1, pady=10, columnspan=2, sticky="e")
        return submitButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancelAuthentication).button
        cancelButton.grid(row=4, column=0, pady=10, sticky="w")
        return cancelButton

    def disablePopup(self):
        self.cancelButton.config(state='disabled')
        self.submitButton.config(state='disabled')
        self.showPasswordButton.config(state='disabled')

    def enablePopup(self):
        self.cancelButton.config(state='normal')
        self.submitButton.config(state='normal')
        self.showPasswordButton.config(state='normal')

    def submitAuthentication(self):
        try:
            text_notification.setText("Signing in...")
            self.disablePopup()
            self.checkAuthentication()
            if self.sessionManager:
                self.sessionManager.login(self.username.get(), self.password.get())
            text_notification.setText(f"Welcome, {self.username.get()}!")
            self.windowRoot.destroy()
        except PasswordExpired:
            text_notification.setText(f"Authentication successful.\nPassword expired, please reset to avoid lockout.")
            PasswordResetScreen(self.RootManager, self.username.get(), True)
            self.windowRoot.destroy()
        except NotAdministratorException:
            text_notification.setText("Authentication failed.\nAdministrator sign in required.")
        except NotSystemAdmin:
            text_notification.setText("Authentication failed.\nSystem administrator sign in required.")
        except IncorrectPasswordException:
            text_notification.setText("Authentication failed.\nIncorrect username/password combination.")
        except PamException as e:
            text_notification.setText(f"Authentication failed.\n{e.message}")
        except UserDoesntExistException:
            text_notification.setText(f"Authentication failed.\n`{self.username.get()}` does not exist.")
        finally:
            if self.windowRoot.winfo_exists() == 1:
                self.enablePopup()

    def cancelAuthentication(self):
        text_notification.setText("Authentication cancelled.")
        self.windowRoot.destroy()

    def togglePassword(self):
        if self.createPasswordEntry.cget('show') == "*":
            self.createPasswordEntry.config(show="")
            self.showPasswordButton.config(text="Hide")
        else:
            self.createPasswordEntry.config(show="*")
            self.showPasswordButton.config(text="Show")

    def checkAuthentication(self):
        validateUserCredentials(self.username.get(), self.password.get())
        userRole = getRole(self.username.get())
        if userRole == UserRole.ADMIN or userRole == UserRole.SYSTEM_ADMIN:
            users = getLockedOutUsers()
            if users:
                LockoutNotification(self.RootManager, users)
        if self.administratorRequired:
            if userRole == UserRole.ADMIN or userRole == UserRole.SYSTEM_ADMIN:
                self.isAuthenticated = True
            else:
                raise NotAdministratorException()
        elif self.systemAdminRequired:
            if userRole == UserRole.SYSTEM_ADMIN:
                self.isAuthenticated = True
            else:
                raise NotSystemAdmin()
        else:
            #  No administrator required, just a user is sufficient
            self.isAuthenticated = True
