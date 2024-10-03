from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class ConnectReaderButton(ButtonInterface):
    def __init__(self, master, invokeFn):
        self.button = ttk.Button(
            master,
            text="Connect Reader",
            style='Default.TButton',
            command=lambda: invokeFn(),
        )

    def hide(self):
        self.button["state"] = "disabled"
        self.button.grid_remove()

    def show(self):
        self.button["state"] = "normal"
        self.button.grid()

