import tkinter as tk
import tkinter.ttk as ttk
from packaging.version import Version

from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.helper_methods.ui_helpers import makeToplevelScrollable
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.popup_interface import PopupInterface


class ReleaseNotes(PopupInterface):
    def __init__(self, releaseNotes, rootManager: RootManager):
        self.releaseNotes = sortNotes(releaseNotes)
        self.download = False
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.windowRoot.transient(rootManager.getRoot())
        self.fonts = FontTheme()
        windowRoot, windowCanvas = makeToplevelScrollable(self.windowRoot, self.fillOutWindowFn)
        rootManager.waitForWindow(self.windowRoot)

    def fillOutWindowFn(self, window):
        row = self.fillInVersions(window)
        self.createDownloadAndCancelButtons(window, row)

    def fillInVersions(self, window):
        row = 0
        tk.Label(window, text="Release Notes", bg='white', font=self.fonts.header1).grid(row=row, column=0,
                                                                                               sticky='w')
        row += 1
        row = self.createSeparatorLine(window, row)
        for version, notes in self.releaseNotes.items():
            tk.Label(window, text=version, bg='white', font=self.fonts.header2).grid(row=row, column=0,
                                                                                           sticky='w')
            row += 1
            row = self.createFeaturesSection(window, notes, row)
            row = self.createBugFixesSection(window, notes, row)
            row = self.createSeparatorLine(window, row)
        return row

    def createFeaturesSection(self, window, notes, row):
        if "features" in notes:
            tk.Label(window, text="New Features:", bg='white', font=self.fonts.header3).grid(row=row,
                                                                                                   column=0,
                                                                                                   sticky='w')
            row += 1
            for index, feature in notes['features'].items():
                tk.Label(window,
                         text=f"- {feature}",
                         bg='white',
                         font=self.fonts.primary2,
                         wraplength=800,
                         justify="left",
                         ).grid(row=row, column=0, sticky='w')
                row += 1
            row = self.createSpacer(window, row)
        return row

    def createBugFixesSection(self, window, notes, row):
        if "bugfixes" in notes:
            tk.Label(window, text="Bug Fixes:", bg='white', font=self.fonts.header3).grid(row=row, column=0,
                                                                                                sticky='w')
            row += 1
            for index, bugfix in notes['bugfixes'].items():
                tk.Label(window,
                         text=f"- {bugfix}",
                         bg='white',
                         font=self.fonts.primary2,
                         wraplength=800,
                         justify="left",
                         ).grid(row=row, column=0, sticky='w')
                row += 1
            row = self.createSpacer(window, row)
        return row

    def createDownloadAndCancelButtons(self, window, row):
        row = self.createSpacer(window, row)
        cancelButton = GenericButton("Cancel", window, lambda: self.setDownload(False)).button
        cancelButton.grid(row=row, column=0, sticky='w')
        downloadButton = GenericButton("Download", window, lambda: self.setDownload(True)).button
        downloadButton.grid(row=row, column=1, sticky='w')

    def setDownload(self, value):
        self.download = value
        self.windowRoot.destroy()

    @staticmethod
    def createSpacer(window, row):
        tk.Label(window, text='', bg='white', font=FontTheme().primary).grid(row=row, column=0, sticky='w')
        row += 1
        return row

    @staticmethod
    def createSeparatorLine(window, row):
        ttk.Separator(window, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew')
        row += 1
        return row


def sortNotes(releaseNotes):
    keys = list(releaseNotes.keys())
    keysWithoutV = [k[1:] for k in keys]
    keysWithoutV.sort(key=Version)
    keys = keysWithoutV[::-1]
    return {f'v{i}': releaseNotes[f'v{i}'] for i in keys}
