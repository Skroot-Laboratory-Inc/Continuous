import platform
import tkinter as tk
from tkinter import ttk

from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.helper_methods.ui_helpers import centerWindowOnFrame
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager


class ConfirmationPopup:
    def __init__(self, rootManager: RootManager, header: str, message: str, altNoText: str = "No", altYesText: str = "Yes"):
        """
        Ask the user to confirm some information before continuing.
        :param rootManager: The RootManager to create the toplevel from.
        :param message: The message to display confirmation of.
        :param header: The header for the dialog box
        :param altNoText: The text to display on the "Do not confirm" button
        :param altYesText: The text to display on the "Confirm" button

        :raises UserConfirmationException: if the user does not confirm the action
        """
        self.confirmed = False
        self.RootManager = rootManager
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.username = tk.StringVar()
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader(header)
        self.createConfirmationMessage(message)
        self.submitButton = self.createConfirmButton(altYesText)
        self.cancelButton = self.createCancelButton(altNoText)

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)
        self.getConfirm()

    def createHeader(self, header: str):
        ttk.Label(
            self.windowRoot,
            text=header,
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew',
                                                                     pady=10)

    def createConfirmationMessage(self, message: str):
        ttk.Label(
            self.windowRoot,
            text=message,
            font=FontTheme().primary2,
            background=Colors().secondaryColor).grid(row=3, column=0, columnspan=3, pady=20)

    def createConfirmButton(self, text: str):
        confirmButton = GenericButton(text, self.windowRoot, self.confirm).button
        confirmButton.grid(row=6, column=1, pady=10, columnspan=2, sticky="e")
        return confirmButton

    def createCancelButton(self, text: str):
        cancelButton = GenericButton(text, self.windowRoot, self.cancel).button
        cancelButton.grid(row=6, column=0, pady=10, sticky="w")
        return cancelButton

    def confirm(self):
        self.confirmed = True
        self.windowRoot.destroy()

    def cancel(self):
        self.confirmed = False
        self.windowRoot.destroy()

    def getConfirm(self):
        if self.confirmed:
            pass
        else:
            raise UserConfirmationException()
