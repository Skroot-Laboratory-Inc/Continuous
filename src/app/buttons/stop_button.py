from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class StopButton(ButtonInterface):
    def __init__(self, master, invokeFn):
        self.stopButton = ttk.Button(
            master,
            text="End Experiment",
            style='W.TButton',
            command=lambda: invokeFn()
        )

    def place(self):
        self.stopButton.pack(side='top', anchor='ne')

    def destroySelf(self):
        self.stopButton.destroy()
