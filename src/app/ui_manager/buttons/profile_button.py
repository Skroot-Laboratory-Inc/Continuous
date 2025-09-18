import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from src.app.authentication.authentication_popup import AuthenticationPopup
from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.image_theme import ImageTheme
from src.app.widget.custom_dropdown import CustomDropdownMenu


class ProfileButton:
    def __init__(self, master, rootManager: RootManager, sessionManager: SessionManager):
        self.master = master
        self.sessionManager = sessionManager
        self.rootManager = rootManager
        image = Image.open(CommonFileManager().getProfileIcon())
        resizedImage = image.resize(ImageTheme().profileSize, Image.Resampling.LANCZOS)
        self.profileIcon = ImageTk.PhotoImage(resizedImage)
        self.button = ttk.Button(
            master,
            text="▼",
            image=self.profileIcon,
            compound=tk.LEFT,
            width=3,
            style='Profile.TButton',
            command=lambda: self.toggleDropdown())

        self.dropdown = CustomDropdownMenu(
            master,
            bg=Colors().primaryColor,
            fg=Colors().secondaryColor,
            font=FontTheme().dropdown,
            relief="solid",
            borderwidth=1,
            min_width=300,
            min_height=200,
            disabledforeground=Colors().secondaryColor,
            border_color="black",
            item_padding_x=25,
            item_padding_y=25,
            item_justify='center',
            separator_color=Colors().secondaryColor
        )

        self.updateDropdownItems()

    def toggleDropdown(self):
        if self.button.cget("text") == "▼":
            self.openDropdown()
        else:
            self.dropdown.unpost()

    def closeDropdown(self):
        self.button.configure(text="▼")
        self.rootManager.getRoot().after(10, lambda: self.setNormal())

    def openDropdown(self):
        self.button["state"] = tk.DISABLED
        self.button.configure(text="▲")
        self.updateDropdownItems()
        self.dropdown.tk_popup(
            x=self.button.winfo_rootx(),
            y=self.button.winfo_rooty() + self.button.winfo_height(),
        )
        self.dropdown.bind("<Unmap>", self.closeDropdown)

    def updateDropdownItems(self):
        self.dropdown.delete(0, 'end')

        if self.sessionManager.isValidSession():
            username = self.sessionManager.getUser()
            self.dropdown.add_command(label=f"User: {username}", state="disabled")
            self.dropdown.add_separator()
            self.dropdown.add_command(label="Sign Out", command=lambda: self.sessionManager.logout())
        else:
            self.dropdown.add_command(label="Not signed in", state="disabled")
            self.dropdown.add_separator()
            self.dropdown.add_command(
                label="Sign In",
                command=lambda: AuthenticationPopup(self.rootManager, self.sessionManager, forceAuthenticate=True),
            )

    def setNormal(self):
        self.button["state"] = tk.NORMAL
