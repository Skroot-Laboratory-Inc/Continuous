from tkinter import ttk
import tkinter as tk


class InformationPanel:
    def __init__(self, AppModule, helpIcon, root):
        self.uploadLogButton = None
        self.AppModule = AppModule
        self.helpIcon = helpIcon
        self.window = tk.Toplevel(root, bg='white', padx=25, pady=25)
        tk.Label(self.window, text="Filler -- images and text will be here to show common problems", bg='white').grid(row=0, column=0, sticky='w')
        self.createUploadLogButton()

    def createUploadLogButton(self):
        self.uploadLogButton = ttk.Button(self.window, text="Didn't solve your problem?", image=self.helpIcon, style='W.TButton',
                                          compound=tk.LEFT, command=lambda: self.uploadLogAndDisable())
        self.uploadLogButton.grid(row=2, column=0, sticky='w')

    def uploadLogAndDisable(self):
        success = self.AppModule.awsUploadLogFile()
        self.uploadLogButton['state'] = 'disabled'
        if success:
            tk.Label(self.window, text="Log sent to Skroot, please contact a representative with more context.", bg='white').grid(row=3, column=0, sticky='w')
        else:
            tk.Label(self.window, text="Please contact a Skroot representative to get more help.", bg='white').grid(row=3, column=0, sticky='w')
