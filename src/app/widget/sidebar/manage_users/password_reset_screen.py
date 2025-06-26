import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.exceptions import PasswordMismatchException, ResetPasswordException, \
    BadPasswordException, SystemAdminException, InsufficientPermissions
from src.app.authentication.helpers.functions import resetPassword, check_password_quality
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification


class PasswordResetScreen:
    def __init__(self, rootManager: RootManager, authorizer: str, forcedReset: bool = False):
        self.authorizer = authorizer
        self.RootManager = rootManager
        self.forcedReset = forcedReset
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.confirmPassword = tk.StringVar()
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.createUsernameEntry = self.createUsername()
        self.createUsernameEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot()))
        if self.forcedReset:
            self.username.set(authorizer)
            self.createUsernameEntry['state'] = tk.DISABLED
            self.createUsernameEntry.unbind("<Button-1>")
        self.createPasswordEntry, self.showPasswordButton = self.createPassword()
        self.createPasswordEntry.bind("<Button-1>",
                                      lambda event: launchKeyboard(event.widget, rootManager.getRoot(), True))
        self.badPasswordLabel = self.createBadPasswordWarning()
        self.confirmPasswordEntry, self.showConfirmPasswordButton = self.createConfirmPassword()
        self.confirmPasswordEntry.bind("<Button-1>",
                                       lambda event: launchKeyboard(event.widget, rootManager.getRoot(), True))
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
            text="Reset Password",
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
        usernameEntry.grid(row=3, column=1, padx=10, ipady=WidgetTheme().entryYPadding)
        return usernameEntry

    def createPassword(self):
        ttk.Label(
            self.windowRoot,
            text="New Password",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=4, column=0)

        passwordEntry = ttk.Entry(self.windowRoot, show="*", width=25, justify="center", background="white",
                                  textvariable=self.password, font=FontTheme().primary)
        passwordEntry.grid(row=4, column=1, padx=10, ipady=WidgetTheme().entryYPadding, pady=10)

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

    def createConfirmPassword(self):
        ttk.Label(
            self.windowRoot,
            text="Confirm Password",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=6, column=0)

        confirmPasswordEntry = ttk.Entry(self.windowRoot, show="*", justify="center", width=25, background="white",
                                         textvariable=self.confirmPassword, font=FontTheme().primary)
        confirmPasswordEntry.grid(row=6, column=1, padx=10, ipady=WidgetTheme().entryYPadding)

        showConfirmPasswordButton = ttk.Button(self.windowRoot, text="Show", command=self.toggleConfirmPassword,
                                               style='Entry.TButton')
        showConfirmPasswordButton.grid(row=6, column=2, pady=10)
        return confirmPasswordEntry, showConfirmPasswordButton

    def createPasswordMismatchWarning(self) -> ttk.Label:
        return ttk.Label(
            self.windowRoot,
            text="",
            wraplength=400,
            font=FontTheme().warning,
            foreground=Colors().lightRed,
            background=Colors().secondaryColor)

    def togglePasswordWarning(self, *args):
        badPassword = False
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

    def createSubmitButton(self):
        submitButton = GenericButton("Submit", self.windowRoot, self.submitReset).button
        submitButton.grid(row=8, column=1, pady=10, columnspan=2, sticky="e")
        submitButton.configure(state="disabled")
        return submitButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancelReset).button
        cancelButton.grid(row=8, column=0, pady=10, sticky="w")
        return cancelButton

    def submitReset(self):
        try:
            self.resetUserPassword()
            self.windowRoot.destroy()
        except PasswordMismatchException:
            text_notification.setText("Password confirmation failed, passwords must match.")
        except BadPasswordException as e:
            text_notification.setText(f"Bad Password\n{e.message}")
        except SystemAdminException as e:
            text_notification.setText(f"Failed to reset password. \n{e.message}")
        except InsufficientPermissions as e:
            text_notification.setText(f"Failed to reset password. \n{e.message}")
        except ResetPasswordException as e:
            text_notification.setText(f"Failed to reset password. \n{e.message}")

    def resetUserPassword(self):
        if self.password.get() != self.confirmPassword.get():
            raise PasswordMismatchException
        resetPassword(self.authorizer, self.username.get(), self.password.get())

    def cancelReset(self):
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
