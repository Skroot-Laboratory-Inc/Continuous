from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class GuidedSetupButton(ButtonInterface):
    def __init__(self, master, invokeFn):
        self.guidedSetupButton = ttk.Button(master, text="Start new experiment", style='W.TButton',
                                            command=lambda: invokeFn())

    def place(self):
        self.guidedSetupButton.grid(row=2, column=1, sticky='se', padx=10, pady=10)

    def destroySelf(self):
        self.guidedSetupButton.destroy()

    def invokeButton(self):
        self.guidedSetupButton.invoke()
