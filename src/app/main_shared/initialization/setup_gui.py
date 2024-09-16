import tkinter as tk
import tkinter.ttk as ttk

from src.app.main_shared.service.dev_software_update import DevSoftwareUpdate
from src.app.main_shared.service.software_update import SoftwareUpdate
from src.app.properties.dev_properties import DevProperties
from src.app.properties.gui_properties import GuiProperties
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.frame_manager import FrameManager
from src.app.ui_manager.root_manager import RootManager
from src.app.theme.colors import Colors
from src.app.widget import text_notification


class SetupGui:
    def __init__(self, rootManager: RootManager, Settings, major_version, minor_version):
        self.Colors = Colors()
        self.RootManager = rootManager
        self.FrameManager = FrameManager(self.RootManager)
        self.Settings = Settings
        self.createTheme()
        self.GuiProperties = GuiProperties()
        self.version = f'{major_version}.{minor_version}'
        self.isDevMode = DevProperties().isDevMode
        if self.isDevMode:
            self.SoftwareUpdate = DevSoftwareUpdate(self.RootManager, major_version, minor_version)
        else:
            self.SoftwareUpdate = SoftwareUpdate(self.RootManager, major_version, minor_version)

    def createMenus(self):
        self.SoftwareUpdate.checkForSoftwareUpdates()
        if self.SoftwareUpdate.newestZipVersion:
            settingsMenuSoftware = self.RootManager.instantiateNewMenubarRibbon()
            settingsMenuSoftware.add_command(
                label="Update",
                command=lambda: self.SoftwareUpdate.downloadSoftwareUpdate())
            self.RootManager.addMenubarCascade("Software", settingsMenuSoftware)

        settingsMenuReaders = self.RootManager.instantiateNewMenubarRibbon()
        settingsMenuReaders.add_command(label="Frequency Range", command=lambda: self.Settings.freqRangeSetting())
        settingsMenuReaders.add_command(label="Scan Rate", command=lambda: self.Settings.rateSetting())
        settingsMenuReaders.add_command(label="File Save", command=lambda: self.Settings.saveFilesSetting())
        self.RootManager.addMenubarCascade("Readers", settingsMenuReaders)

    def createDisplayMenus(self):
        settingsMenuDisplay = self.RootManager.instantiateNewMenubarRibbon()
        settingsMenuDisplay.add_command(label="SGI", command=lambda: self.Settings.freqToggleSetting("SGI"))
        settingsMenuDisplay.add_command(label="Signal Check",
                                        command=lambda: self.Settings.freqToggleSetting("Signal Check"))
        self.RootManager.addMenubarCascade("Display", settingsMenuDisplay)

    def createFrames(self):
        footer = self.FrameManager.createFooterFrame()
        versionLabel = tk.Label(footer, text=f'Version: v{self.version}', bg='white')
        versionLabel.place(relx=0.0, rely=1.0, anchor='sw')
        copyrightLabel = tk.Label(
            footer,
            text='\u00A9 Skroot Laboratory, Inc 2018-2024. All rights reserved.',
            bg='white')
        copyrightLabel.place(relx=0.5, rely=1.0, anchor='s')

        bodyFrame = self.FrameManager.createBodyFrame()
        bodyFrame.place(
            relx=0,
            rely=self.GuiProperties.bodyRelY,
            relwidth=1,
            relheight=self.GuiProperties.bodyHeight)

        textFrame = self.FrameManager.createBannerFrame()
        text_notification.createWidget(textFrame)
        text_notification.setText("Skroot Laboratory - Follow the prompts to get started.")
        text_notification.packWidget()
        return bodyFrame

    def createTheme(self):
        self.RootManager.setTitle("Skroot Reader GUI")
        style = ttk.Style()
        style.theme_use('clam')
        self.RootManager.setBackgroundColor(self.Colors.secondaryColor)
        style.configure(
            'W.TButton',
            font=FontTheme().buttons,
            foreground=self.Colors.secondaryColor,
            background=self.Colors.primaryColor)
        style.map(
            'W.TButton',
            background=[("disabled", "gray23"), ("active", self.Colors.primaryColor)])
