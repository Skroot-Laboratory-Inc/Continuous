import tkinter as tk
from tkinter import ttk

from src.app.aws.aws import AwsBoto3
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.root_manager import RootManager
from src.app.theme.colors import Colors


class InformationPanel:
    def __init__(self, helpIcon, rootManager: RootManager):
        self.uploadLogButton = None
        self.AwsBoto3Service = AwsBoto3()
        self.CommonFileManager = CommonFileManager()
        self.helpIcon = helpIcon
        self.Colors = Colors()
        self.window = rootManager.createTopLevel()
        self.createUploadLogButton()

    def createUploadLogButton(self):
        self.uploadLogButton = ttk.Button(self.window, text="Send experiment log to Skroot.", image=self.helpIcon, style='Help.TButton',
                                          compound=tk.LEFT, command=lambda: self.uploadLogAndDisable())
        self.uploadLogButton.grid(row=2, column=0, sticky='w')

    def uploadExperimentLog(self):
        return self.AwsBoto3Service.uploadFile(
            self.CommonFileManager.getExperimentLog(),
            'text/plain',
            tags={"response_email": "greenwalt@skrootlab.com"}
        )

    def uploadLogAndDisable(self):
        success = self.uploadExperimentLog()
        self.uploadLogButton['state'] = 'disabled'
        if success:
            tk.Label(self.window, text="Experiment log has been sent to Skroot. \nPlease contact a Skroot representative with more context.", bg='white').grid(row=3, column=0, sticky='w')
        else:
            tk.Label(self.window, text="Experiment Log failed to upload \nPlease contact a Skroot representative to get more help.", bg='white').grid(row=3, column=0, sticky='w')
