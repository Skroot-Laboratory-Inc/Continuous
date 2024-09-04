import tkinter.font
from tkinter import ttk


class Linkbutton(ttk.Button):
    def __init__(self, *args, font: tkinter.font.Font, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = font
        style = ttk.Style()
        style.configure("Link.TLabel", foreground="#357fde", font=self.font, background='white', highlightthickness=0,
                                        borderwidth=0)
        self.configure(style="Link.TLabel", cursor="hand2")

