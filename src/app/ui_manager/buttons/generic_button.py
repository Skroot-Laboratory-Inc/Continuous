from tkinter import ttk


class GenericButton:
    def __init__(self, text: str, master, invokeFn):
        self.invokeFn = invokeFn
        self.button = ttk.Button(
            master,
            text=text,
            style='Default.TButton',
            command=lambda: invokeFn(),
        )

    def invoke(self):
        self.hide()
        self.invokeFn()

    def hide(self):
        self.button.configure(state="disabled")
        self.button.grid_remove()

    def disable(self):
        self.button.configure(state="disabled")

    def enable(self):
        self.button.configure(state="normal")

    def show(self):
        self.button.configure(state="normal")
        self.button.grid()
