import tkinter as tk
from tkinter import ttk


class InformationPanel:
    def __init__(self, AppModule, helpIcon, root):
        self.uploadLogButton = None
        self.AppModule = AppModule
        self.helpIcon = helpIcon
        self.window = tk.Toplevel(root, bg='white', padx=25, pady=25)
        self.createUploadLogButton()

    def createUploadLogButton(self):
        self.uploadLogButton = ttk.Button(self.window, text="Send experiment log to Skroot.", image=self.helpIcon, style='W.TButton',
                                          compound=tk.LEFT, command=lambda: self.uploadLogAndDisable())
        self.uploadLogButton.grid(row=2, column=0, sticky='w')

    def uploadLogAndDisable(self):
        success = self.AppModule.awsUploadLogFile()
        self.uploadLogButton['state'] = 'disabled'
        if success:
            tk.Label(self.window, text="Experiment log has been sent to Skroot. \nPlease contact a Skroot representative with more context.", bg='white').grid(row=3, column=0, sticky='w')
        else:
            tk.Label(self.window, text="Experiment Log failed to upload \nPlease contact a Skroot representative to get more help.", bg='white').grid(row=3, column=0, sticky='w')
