from tkinter import ttk
from tkinter.font import Font, nametofont


class Linkbutton(ttk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use the default font.
        label_font = nametofont("TkDefaultFont").cget("family")
        self.font = Font(family=label_font, size=9)
        # Label-like styling.
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