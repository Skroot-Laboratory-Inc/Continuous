import tkinter as tk
import tkinter.ttk as ttk

from src.app.buttons.help_button import HelpButton
from src.app.buttons.power_button import PowerButton
from src.app.main_shared.service.dev_software_update import DevSoftwareUpdate
from src.app.main_shared.service.software_update import SoftwareUpdate
from src.app.properties.dev_properties import DevProperties
from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.main_shared.initialization.frame_manager import FrameManager
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification


class SetupBaseUi:
    def __init__(self, rootManager: RootManager, major_version, minor_version):
        self.Colors = Colors()
        self.RootManager = rootManager
        self.isDevMode = DevProperties().isDevMode
        if self.isDevMode:
            self.SoftwareUpdate = DevSoftwareUpdate(self.RootManager, major_version, minor_version)
        else:
            self.SoftwareUpdate = SoftwareUpdate(self.RootManager, major_version, minor_version)
        self.FrameManager = FrameManager(self.RootManager)
        self.GuiProperties = GuiProperties()
        self.version = f'{major_version}.{minor_version}'
        self.bodyFrame = self.createFrames()
        self.createMenus()
        self.createTheme()

    def createMenus(self):
        self.SoftwareUpdate.checkForSoftwareUpdates()
        if self.SoftwareUpdate.newestZipVersion:
            settingsMenuSoftware = self.RootManager.instantiateNewMenubarRibbon()
            settingsMenuSoftware.add_command(
                label="Update",
                command=lambda: self.SoftwareUpdate.downloadSoftwareUpdate())
            self.RootManager.addMenubarCascade("Software", settingsMenuSoftware)

    def createFrames(self):
        versionLabel = tk.Label(self.FrameManager.footerFrame, text=f'Version: v{self.version}', bg='white')
        versionLabel.place(relx=0.0, rely=1.0, anchor='sw')
        copyrightLabel = tk.Label(
            self.FrameManager.footerFrame,
            text='\u00A9 Skroot Laboratory, Inc 2018-2024. All rights reserved.',
            bg='white')
        copyrightLabel.place(relx=0.5, rely=1.0, anchor='s')
        helpButton = HelpButton(self.FrameManager.footerFrame, self.RootManager)
        helpButton.helpButton.place(relx=1, rely=1.0, anchor='se')

        self.FrameManager.bannerFrame.grid_columnconfigure(0, weight=1)
        self.FrameManager.bannerFrame.grid_columnconfigure(1, weight=0)
        widget = text_notification.createWidget(self.FrameManager.bannerFrame)
        text_notification.setText("Skroot Laboratory - Follow the prompts to get started.")
        widget.grid(row=0, column=0, sticky='nsew')
        powerButton = PowerButton(self.FrameManager.bannerFrame).button
        powerButton.grid(row=0, column=1)
        return self.FrameManager.bodyFrame

    def createTheme(self):
        self.RootManager.setTitle("Skroot Reader GUI")
        style = ttk.Style()
        style.theme_use('clam')
        self.RootManager.setBackgroundColor(self.Colors.secondaryColor)
        style.configure(
            'Default.TButton',
            font=FontTheme().buttons,
            foreground=self.Colors.secondaryColor,
            background=self.Colors.primaryColor)
        style.configure(
            'Help.TButton',
            font=('Helvetica', 9),
            foreground=self.Colors.secondaryColor,
            background=self.Colors.primaryColor)
        style.map(
            'Default.TButton',
            background=[("disabled", "gray23"), ("active", self.Colors.primaryColor)])
        style.map(
            'Help.TButton',
            background=[("disabled", "gray23"), ("active", self.Colors.primaryColor)])

