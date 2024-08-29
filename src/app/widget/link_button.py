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
        self.bind("<Enter>", self.on_mouse_enter)
        self.bind("<Leave>", self.on_mouse_leave)

    def on_mouse_enter(self, event):
        self.font.configure(underline=True)

    def on_mouse_leave(self, event):
        self.font.configure(underline=False)