import platform
import tkinter as tk
from tkinter import ttk
from typing import List

from src.app.authentication.helpers.functions import clearLockedOutUsers
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, formatPopup
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme


class LockoutNotification:
    def __init__(self, rootManager: RootManager, usersLocked: List[str]):
        self.usersLocked = usersLocked
        self.RootManager = rootManager
        self.windowRoot = rootManager.createTopLevel()
        formatPopup(self.windowRoot)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader()
        self.createNotification()
        self.submitButton = self.createConfirmButton()
        self.cancelButton = self.createCancelButton()

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Warning: Users Locked Out",
            font=FontTheme().header1,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createNotification(self):
        ttk.Label(
            self.windowRoot,
            text="".join(self.usersLocked),
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=1, column=0, columnspan=3)

    def createConfirmButton(self):
        submitButton = GenericButton("Confirm", self.windowRoot, self.confirm).button
        submitButton.grid(row=4, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        return submitButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=4, column=0, pady=WidgetTheme().externalPadding, sticky="w")
        return cancelButton

    def confirm(self):
        clearLockedOutUsers()
        self.windowRoot.destroy()

    def cancel(self):
        self.windowRoot.destroy()
