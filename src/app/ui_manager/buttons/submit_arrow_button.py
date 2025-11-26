import tkinter as tk
from typing import Callable

from PIL import Image, ImageTk

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.image_theme import ImageTheme


class SubmitArrowButton:
    def __init__(self, master, invokeFn: Callable):
        commonFileManager = CommonFileManager()
        image = Image.open(commonFileManager.getArrowIcon())
        resizedImage = image.resize(ImageTheme().arrowSize, Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(resizedImage)
        self.invokeFn = invokeFn

        self.button = tk.Button(
            master,
            bg=Colors().body.background,
            highlightthickness=0,
            borderwidth=0,
            image=self.image,
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

