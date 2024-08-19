from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class CalibrateReadersButton(ButtonInterface):
    def __init__(self, master, invokeFn):
        self.calibrateReadersButton = ttk.Button(
            master,
            text="Calibrate",
            style='W.TButton',
            command=lambda: invokeFn(),
        )

    def place(self):
        self.calibrateReadersButton.place(relx=0.46, rely=0.47)

    def destroySelf(self):
        self.calibrateReadersButton.destroy()
