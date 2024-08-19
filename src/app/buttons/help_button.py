from tkinter import ttk
import tkinter as tk

from PIL import Image, ImageTk

from src.app.buttons.button_interface import ButtonInterface
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.widget.information_panel import InformationPanel


class HelpButton(ButtonInterface):
    def __init__(self, root, AppModule):
        fileManager = CommonFileManager()
        image = Image.open(fileManager.getHelpIcon())
        resizedImage = image.resize((15, 15), Image.LANCZOS)
        self.helpIcon = ImageTk.PhotoImage(resizedImage)
        self.root = root
        self.AppModule = AppModule
        self.helpButton = ttk.Button(
            root,
            text="Need help?",
            image=self.helpIcon,
            compound=tk.LEFT,
            style='W.TButton',
            command=lambda: self.invoke())

    def place(self):
        self.helpButton.pack(side='bottom', anchor='se')

    def invoke(self):
        InformationPanel(self.AppModule, self.helpIcon, self.root)

    def destroySelf(self):
        self.helpButton.destroy()
