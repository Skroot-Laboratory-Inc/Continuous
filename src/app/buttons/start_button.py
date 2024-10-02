from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class StartButton(ButtonInterface):
    def __init__(self, master, invokeFn):
        self.startButton = ttk.Button(
            master,
            text="Start",
            style='Default.TButton',
            command=lambda: invokeFn(),
        )
