import glob
import logging
import platform
import tkinter as tk
from tkinter import ttk

from src.app.authentication.helpers.logging import logAuthAction
from src.app.custom_exceptions.common_exceptions import USBDriveNotFoundException
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.helper_functions import getUsbDrive, unmountUSBDrive
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification
from src.app.widget.sidebar.helpers.functions import copyRunFile


class RunExporter:
    def __init__(self, rootManager: RootManager, exportedBy: str = "", runId: str = ""):
        self.RootManager = rootManager
        self.exportedBy = exportedBy
        self.windowRoot = rootManager.createTopLevel()
        self.windowRoot.config(relief="solid", highlightbackground="black",
                               highlightcolor="black", highlightthickness=1, bd=0)
        self.runIdVar = tk.StringVar(value=runId)
        self.windowRoot.transient(rootManager.getRoot())
        self.createHeader()
        self.runIdEntry = self.createRunID()
        self.runIdEntry.bind("<Button-1>", lambda event: launchKeyboard(event.widget, rootManager.getRoot(), "Run ID:  "))
        self.downloadButton = self.createDownloadButton()
        self.cancelButton = self.createCancelButton()
        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        ttk.Label(
            self.windowRoot,
            text="Export Run Data",
            font=FontTheme().header1,
            background=Colors().secondaryColor).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createRunID(self):
        ttk.Label(
            self.windowRoot,
            text="Run ID",
            font=FontTheme().primary,
            background=Colors().secondaryColor).grid(row=3, column=0)

        vesselIdEntry = ttk.Entry(self.windowRoot, width=25, background="white", justify="center",
                                  textvariable=self.runIdVar, font=FontTheme().primary)
        vesselIdEntry.grid(row=3, column=1, padx=10, ipady=WidgetTheme().internalPadding, pady=WidgetTheme().externalPadding)
        return vesselIdEntry

    def createDownloadButton(self):
        if platform.system() == "Linux":
            downloadButton = GenericButton("Download", self.windowRoot, self.download).button
        else:
            downloadButton = GenericButton("Download", self.windowRoot, self.downloadWindows).button
        downloadButton.grid(row=6, column=1, pady=WidgetTheme().externalPadding, columnspan=2, sticky="e")
        return downloadButton

    def createCancelButton(self):
        cancelButton = GenericButton("Cancel", self.windowRoot, self.cancel).button
        cancelButton.grid(row=6, column=0, pady=WidgetTheme().externalPadding, sticky="w")
        return cancelButton

    def cancel(self):
        self.windowRoot.destroy()

    def downloadWindows(self):
        vesselId = self.runIdEntry.get()
        try:
            copyRunFile(self.exportedBy, "H:\\", vesselId)
            self.windowRoot.destroy()
        except:
            text_notification.setText(f"Failed to copy run data for {vesselId}.")
            logging.exception("Failed to create batch log on drive.", extra={"id": "Batch Log"})

    def download(self):
        runId = self.runIdEntry.get()
        try:
            if glob.glob(f"{CommonFileManager().getDataSavePath()}/*_{runId}") and runId != "":
                driveLocation = getUsbDrive()
                logAuthAction("Experiment Data Export", "Initiated", self.exportedBy, extra=runId)
                copyRunFile(self.exportedBy, driveLocation, runId)
                text_notification.setText(f"Experiment data for {runId} exported to USB drive.")
                logAuthAction("Experiment Data Export", "Successful", self.exportedBy, extra=runId)
                self.windowRoot.destroy()
            else:
                text_notification.setText(f"No data found for {runId}")
        except USBDriveNotFoundException:
            text_notification.setText(f"USB drive not found. Plug in a USB and try again.")
            logging.exception("USB Drive not found.", extra={"id": "Batch Log"})
        except:
            logAuthAction("Experiment Data Export", "Failed", self.exportedBy, extra=runId)
            text_notification.setText(f"Failed to copy run data for {runId}.")
            logging.exception("Failed to create batch log on drive.", extra={"id": "Batch Log"})
        finally:
            unmountUSBDrive()
