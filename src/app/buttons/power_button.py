import subprocess
import tkinter as tk
from tkinter import messagebox
from typing import Callable

from PIL import Image, ImageTk

from src.app.buttons.button_interface import ButtonInterface
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper.helper_functions import confirmAndPowerDown
from src.app.theme.colors import Colors


class PowerButton(ButtonInterface):
    def __init__(self, master):
        commonFileManager = CommonFileManager()
        image = Image.open(commonFileManager.getPowerIcon())
        resizedImage = image.resize((50, 50), Image.Resampling.LANCZOS)
        self.powerIcon = ImageTk.PhotoImage(resizedImage)

        self.button = tk.Button(
            master,
            bg=Colors().primaryColor,
            highlightthickness=0,
            activebackground=Colors().primaryColor,
            borderwidth=0,
            padx=0,
            pady=0,
            image=self.powerIcon,
            command=lambda: self.invoke())

    def invoke(self):
        self.button["state"] = "disabled"
        confirmAndPowerDown()
        self.button["state"] = "normal"

    def hide(self):
        self.button["state"] = "disabled"
        self.button.grid_remove()

    def show(self):
        self.button["state"] = "normal"
        self.button.grid()
        self.button.tkraise()

