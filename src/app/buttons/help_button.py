from tkinter import ttk
import tkinter as tk

from PIL import Image, ImageTk

from src.app.buttons.button_interface import ButtonInterface
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.information_panel import InformationPanel


class HelpButton(ButtonInterface):
    def __init__(self, master, rootManager: RootManager):
        fileManager = CommonFileManager()
        image = Image.open(fileManager.getHelpIcon())
        resizedImage = image.resize((15, 15), Image.Resampling.LANCZOS)
        self.helpIcon = ImageTk.PhotoImage(resizedImage)
        self.RootManager = rootManager
        self.helpButton = ttk.Button(
            master,
            text="Need help?",
            image=self.helpIcon,
            compound=tk.LEFT,
            style='Help.TButton',
            command=lambda: self.invoke())

    def place(self):
        self.helpButton.pack(side='bottom', anchor='se')

    def invoke(self):
        InformationPanel(self.helpIcon, self.RootManager)
