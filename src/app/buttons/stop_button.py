from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class StopButton(ButtonInterface):
    def __init__(self, master, invokeFn):
        self.stopButton = ttk.Button(
            master,
            text="Stop",
            style='Default.TButton',
            command=lambda: invokeFn()
        )