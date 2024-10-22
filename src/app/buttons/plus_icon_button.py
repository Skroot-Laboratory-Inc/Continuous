import tkinter as tk
from typing import Callable

from PIL import Image, ImageTk

from src.app.buttons.button_interface import ButtonInterface
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.theme.colors import Colors


class PlusIconButton(ButtonInterface):
    def __init__(self, master, invokeFn: Callable):
        commonFileManager = CommonFileManager()
        image = Image.open(commonFileManager.getAddIcon())
        resizedImage = image.resize((200, 200), Image.Resampling.LANCZOS)
        self.createIcon = ImageTk.PhotoImage(resizedImage)
        self.invokeFn = invokeFn

        self.button = tk.Button(
            master,
            bg=Colors().secondaryColor,
            highlightthickness=0,
            borderwidth=0,
            image=self.createIcon,
            command=lambda: self.invoke())

    def invoke(self):
        self.button["state"] = "disabled"
        self.invokeFn()
        self.button["state"] = "normal"

    def hide(self):
        self.button["state"] = "disabled"
        self.button.grid_remove()

    def show(self):
        self.button["state"] = "normal"
        self.button.grid()
        self.button.tkraise()

