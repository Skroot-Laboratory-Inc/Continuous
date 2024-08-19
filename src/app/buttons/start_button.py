from tkinter import ttk

from src.app.buttons.button_interface import ButtonInterface


class StartButton(ButtonInterface):
    def __init__(self, master, invokeFn):
        self.startButton = ttk.Button(
            master,
            text="Start Experiment",
            style='W.TButton',
            command=lambda: invokeFn(),
        )

    def place(self):
        self.startButton.place(relx=0.46, rely=0.47)

    def destroySelf(self):
        self.startButton.destroy()
