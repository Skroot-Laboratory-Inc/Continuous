import logging
import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.exceptions import PasswordMismatchException, UserExistsException, \
    BadPasswordException
from src.app.authentication.helpers.functions import createKioskAdmin, createKioskUser, check_password_quality
from src.app.authentication.helpers.logging import logAuthAction
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard, createDropdown
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification


class UserRegistration:
    def __init__(self, rootManager: RootManager, adminUser: str):
        self.adminUser = adminUser
        self.RootManager = rootManager
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.confirmPassword = tk.StringVar()
        self.role = tk.StringVar(value="Administrator")
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.createRole()
        self.createUsernameEntry = self.createUsername()
        self.createUsernameEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Username:  "))
        self.createPasswordEntry, self.showPasswordButton = self.createPassword()
        self.createPasswordEntry.bind("<Button-1>",
                                      lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Password:  ",True))
        self.badPasswordLabel = self.createBadPasswordWarning()
        self.confirmPasswordEntry, self.showConfirmPasswordButton = self.createConfirmPassword()
        self.confirmPasswordEntry.bind("<Button-1>",
                                       lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Confirm Password:  ",True))
        self.passwordMismatchLabel = self.createBadPasswordWarning()
        self.password.trace_add("write", self.togglePasswordWarning)
        self.confirmPassword.trace_add("write", self.togglePasswordWarning)
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
            text="User Registration",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createRole(self):
        ttk.Label(
            self.windowRoot,
            text="Role",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=2, column=0)
        options = ["Administrator", "User"]
        dropdown = createDropdown(self.windowRoot, self.role, options, outline=True)
        dropdown.grid(row=2, column=1, padx=10, ipady=WidgetTheme().internalPadding, sticky="ew", pady=WidgetTheme().externalPadding)

    def createUsername(self):
        ttk.Label(
            self.windowRoot,
            text="Username",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=3, column=0)

        usernameEntry = ttk.Entry(self.windowRoot, width=25, background="white", justify="center",
                                  textvariable=self.username, font=FontTheme().primary)
        usernameEntry.grid(row=3, column=1, padx=10, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding)
        return usernameEntry

    def createPassword(self):
        ttk.Label(
            self.windowRoot,
            text="Password",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=4, column=0)

        passwordEntry = ttk.Entry(self.windowRoot, show="*", width=25, justify="center", background="white",
                                  textvariable=self.password, font=FontTheme().primary)
        passwordEntry.grid(row=4, column=1, padx=10, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding)

        showPasswordButton = ttk.Button(self.windowRoot, text="Show", command=self.togglePassword,
                                        style='Entry.TButton')
        showPasswordButton.grid(row=4, column=2)
        return passwordEntry, showPasswordButton

    def createBadPasswordWarning(self) -> ttk.Label:
        return ttk.Label(
            self.windowRoot,
            text="",
            wraplength=400,
            font=FontTheme().warning,
            foreground=Colors().lightRed,
            background=Colors().secondaryColor)

    def togglePasswordWarning(self, *args):
        badPassword = False
        if not self.password.get():
            badPassword = True
        goodPassword, message = check_password_quality(self.username.get(), self.password.get())
        if not goodPassword:
            badPassword = True
            self.badPasswordLabel.configure(text=f"*{message}")
            self.badPasswordLabel.grid(row=5, column=1, columnspan=2, sticky="w")
        else:
            self.badPasswordLabel.grid_forget()
        if self.password.get() != self.confirmPassword.get():
            badPassword = True
            self.passwordMismatchLabel.configure(text="*Password confirmation failed, passwords must match.")
            self.passwordMismatchLabel.grid(row=7, column=1, columnspan=2, sticky="w")
        else:
            self.passwordMismatchLabel.grid_forget()
        if badPassword:
            self.submitButton.configure(state="disabled")
        else:
            self.submitButton.configure(state="normal")

    def createConfirmPassword(self):
        ttk.Label(
            self.windowRoot,
            text="Confirm Password",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=6, column=0)

        confirmPasswordEntry = ttk.Entry(self.windowRoot, show="*", justify="center", width=25, background="white",
                                         textvariable=self.confirmPassword, font=FontTheme().primary)
        confirmPasswordEntry.grid(row=6, column=1, padx=10, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding)

        showConfirmPasswordButton = ttk.Button(self.windowRoot, text="Show", command=self.toggleConfirmPassword,
                                               style='Entry.TButton')
        showConfirmPasswordButton.grid(row=6, column=2, pady=WidgetTheme().externalPadding)
        return confirmPasswordEntry, showConfirmPasswordButton

    def createPasswordMismatchWarning(self) -> ttk.Label:
        return ttk.Label(
            self.windowRoot,
            text="",
            wraplength=400,
            font=FontTheme().warning,
            foreground=Colors().lightRed,
            background=Colors().secondaryColor)

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitAuthentication).button
        submitButton.grid(row=8, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        submitButton.configure(state="disabled")
        return submitButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancelAuthentication).button
        cancelButton.grid(row=8, column=0, pady=WidgetTheme().externalPadding, sticky="w")
        return cancelButton

    def submitAuthentication(self):
        try:
            self.registerUser()
            self.windowRoot.destroy()
        except PasswordMismatchException:
            text_notification.setText("Password confirmation failed, passwords must match.")
        except BadPasswordException:
            pass
        except UserExistsException:
            pass

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

    def toggleConfirmPassword(self):
        if self.confirmPasswordEntry.cget('show') == "*":
            self.confirmPasswordEntry.config(show="")
            self.showConfirmPasswordButton.config(text="Hide")
        else:
            self.confirmPasswordEntry.config(show="*")
            self.showConfirmPasswordButton.config(text="Show")

    def registerUser(self):
        logAuthAction(
            "User Registration",
            "Initiated",
            self.username.get(),
            authorizer=self.adminUser,
        )

        try:
            if self.role.get().strip() == "Administrator":
                returnCode = createKioskAdmin(self.username.get(), self.password.get())
            else:
                returnCode = createKioskUser(self.username.get(), self.password.get())

            if returnCode == 0:
                logAuthAction(
                    "User Registration",
                    "Successful",
                    self.username.get(),
                    authorizer=self.adminUser,
                    result=f"{self.role.get().strip()} '{self.username.get()}' was created.",
                )
                text_notification.setText(f"Successfully registered {self.role.get().strip()}: {self.username.get()}")
            else:
                logAuthAction(
                    "User Registration",
                    "Failed",
                    self.username.get(),
                    authorizer=self.adminUser,
                )
                text_notification.setText(f"Error creating user: {self.username.get()}")
                logging.info(
                    f"Failed to create `{self.username.get()}` by {self.adminUser}. Return code: {returnCode}",
                    extra={"id": "auth"})
        except UserExistsException as e:
            logAuthAction(
                "User Registration",
                "Failed",
                self.username.get(),
                authorizer=self.adminUser,
                extra="User Already Exists",
            )
            text_notification.setText(f"Username already exists: {self.username.get()}")
            logging.exception(f"Failed to create `{self.username.get()}` by {self.adminUser}.", extra={"id": "auth"})
            raise e
        except BadPasswordException as e:
            logAuthAction(
                "User Registration",
                "Failed",
                self.username.get(),
                authorizer=self.adminUser,
                extra="Bad Password",
            )
            text_notification.setText("Bad Password")
            logging.exception(f"Failed to create `{self.username.get()}` by {self.adminUser}.", extra={"id": "auth"})
            raise e
        except Exception as e:
            logAuthAction("User Registration", "Failed", self.username.get(), authorizer=self.adminUser)
            text_notification.setText(f"Error creating user: {self.username.get()}")
            logging.exception(f"Failed to create `{self.username.get()}` by {self.adminUser}.", extra={"id": "auth"})
            raise
