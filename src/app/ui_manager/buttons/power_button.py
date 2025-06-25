import tkinter as tk

from PIL import Image, ImageTk

from src.app.authentication.helpers.decorators import requireUser
from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.helper_functions import restartPc
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.image_theme import ImageTheme
from src.app.widget.confirmation_popup import ConfirmationPopup


class PowerButton:
    def __init__(self, master, rootManager: RootManager, sessionManager: SessionManager):
        image = Image.open(CommonFileManager().getPowerIcon())
        resizedImage = image.resize(ImageTheme().powerSize, Image.Resampling.LANCZOS)
        self.powerIcon = ImageTk.PhotoImage(resizedImage)
        self.rootManager = rootManager
        self.sessionManager = sessionManager

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
        self.button.configure(state="disabled")
        self.confirmAndRestart()
        self.button.configure(state="normal")

    def hide(self):
        self.button.configure(state="disabled")
        self.button.grid_remove()

    def show(self):
        self.button.configure(state="normal")
        self.button.grid()
        self.button.tkraise()

    @requireUser
    def confirmAndRestart(self):
        """ Prompts the user to confirm that they would like to restart, then restarts the pi. """
        try:
            ConfirmationPopup(
                self.rootManager,
                'Reboot Reader',
                'Are you sure you wish to restart the system?',
            )
            restartPc()
        except UserConfirmationException:
            pass
