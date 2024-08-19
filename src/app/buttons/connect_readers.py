from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class ConnectReadersButton(ButtonInterface):
    def __init__(self, master, invokeFn, numReaders):
        self.connectReadersButton = ttk.Button(
            master,
            text="Connect Readers",
            style='W.TButton',
            command=lambda: invokeFn(numReaders),
        )

    def place(self):
        self.connectReadersButton.place(relx=0.46, rely=0.47)

    def destroySelf(self):
        self.connectReadersButton.destroy()