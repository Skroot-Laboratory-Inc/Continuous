import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.image_theme import ImageTheme
from src.app.widget.sidebar.manuals.troubleshooting_page import TroubleshootingPage


class HelpButton:
    def __init__(self, master, rootManager: RootManager):
        fileManager = CommonFileManager()
        image = Image.open(fileManager.getHelpIcon())
        resizedImage = image.resize(ImageTheme().helpSize, Image.Resampling.LANCZOS)
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
        self.helpButton["state"] = "disabled"
        TroubleshootingPage(self.RootManager)
        self.helpButton["state"] = "normal"

