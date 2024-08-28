import tkinter as tk
from tkinter import ttk

from src.app.ui_manager.root_manager import RootManager
from src.app.theme.colors import Colors


class InformationPanel:
    def __init__(self, AppModule, helpIcon, rootManager: RootManager):
        self.uploadLogButton = None
        self.AppModule = AppModule
        self.helpIcon = helpIcon
        self.Colors = Colors()
        self.window = rootManager.createTopLevel()
        self.createUploadLogButton()

    def createUploadLogButton(self):
        self.uploadLogButton = ttk.Button(self.window, text="Send experiment log to Skroot.", image=self.helpIcon, style='W.TButton',
                                          compound=tk.LEFT, command=lambda: self.uploadLogAndDisable())
        self.uploadLogButton.grid(row=2, column=0, sticky='w')

    def uploadLogAndDisable(self):
        success = self.AppModule.MainThreadManager.AwsService.uploadExperimentLog()
        self.uploadLogButton['state'] = 'disabled'
        if success:
            tk.Label(self.window, text="Experiment log has been sent to Skroot. \nPlease contact a Skroot representative with more context.", bg='white').grid(row=3, column=0, sticky='w')
        else:
            tk.Label(self.window, text="Experiment Log failed to upload \nPlease contact a Skroot representative to get more help.", bg='white').grid(row=3, column=0, sticky='w')
