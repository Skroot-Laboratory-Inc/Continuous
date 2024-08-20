from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class GuidedSetupButton(ButtonInterface):
    def __init__(self, master, AppModule):
        self.AppModule = AppModule
        self.guidedSetupButton = ttk.Button(master, text="Start new experiment", style='W.TButton',
                                            command=lambda: self.invoke())

    def place(self):
        self.guidedSetupButton.grid(row=2, column=1, sticky='se', padx=10, pady=10)

    def invoke(self):
        self.AppModule.guidedSetup(
            self.AppModule.month,
            self.AppModule.day,
            self.AppModule.year,
            self.AppModule.numReaders,
            self.AppModule.scanRate,
            self.AppModule.experimentId,
            self.AppModule.secondAxisTitle,
            self.AppModule.equilibrationTime)

    def destroySelf(self):
        self.guidedSetupButton.destroy()
