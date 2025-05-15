import tkinter as tk
from tkinter import ttk

from src.app.aws.aws import AwsBoto3
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.ui_helpers import centerWindowOnFrame
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.theme.colors import Colors


class InformationPanel:
    def __init__(self, helpIcon, rootManager: RootManager):
        self.window = rootManager.createTopLevel()
        self.window.grab_set()
        self.window.grid_columnconfigure(0, weight=1, minsize=35)
        self.window.grid_columnconfigure(1, weight=9, minsize=100)
        self.window.grid_columnconfigure(2, weight=1, minsize=35)
        self.AwsBoto3Service = AwsBoto3()
        self.CommonFileManager = CommonFileManager()
        self.helpIcon = helpIcon
        self.Colors = Colors()
        self.populateText()
        self.uploadLogButton = self.createUploadLogButton()
        self.cancelButton = self.createCancelButton()
        centerWindowOnFrame(self.window, rootManager.getRoot())

    def populateText(self):
        tk.Label(
            self.window,
             text=f"Experiencing technical difficulties? Let our team help. "
                  f"Email a Skroot representative describing the issue you are facing, "
                  f"and send the application log to us. We'll handle the rest.",
             bg='white',
             font=FontTheme().primary,
             wraplength=500,
             justify="center",
         ).grid(row=0, column=0, columnspan=3, sticky='w')

    def createUploadLogButton(self):
        uploadLogButton = ttk.Button(self.window, text="Send", image=self.helpIcon, style='Help.TButton',
                                          compound=tk.LEFT, command=lambda: self.uploadLogAndDisable())
        uploadLogButton.grid(row=2, column=0, sticky='w')
        return uploadLogButton

    def createCancelButton(self):
        cancelButton = ttk.Button(self.window, text="Cancel", command=lambda: self.window.destroy(),
                                  style='Default.TButton')
        cancelButton.grid(row=2, column=2, sticky='w')
        return cancelButton

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
