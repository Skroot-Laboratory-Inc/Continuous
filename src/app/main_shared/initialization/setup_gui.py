import tkinter as tk
import tkinter.ttk as ttk

from src.app.properties.gui_properties import GuiProperties
from src.app.ui_manager.frame_manager import FrameManager
from src.app.ui_manager.root_manager import RootManager
from src.app.theme.colors import Colors
from src.app.widget import text_notification


class SetupGui:
    def __init__(self, rootManager: RootManager, Settings, AppModule):
        self.Colors = Colors()
        self.RootManager = rootManager
        self.FrameManager = FrameManager(self.RootManager)
        self.Settings = Settings
        self.AppModule = AppModule
        self.createTheme()
        self.GuiProperties = GuiProperties()

    def createMenus(self):
        self.AppModule.MainThreadManager.AwsService.checkForSoftwareUpdate()
        menubar = self.RootManager.instantiateMenubar()
        if self.AppModule.MainThreadManager.AwsService.SoftwareUpdate.newestZipVersion:
            settingsMenuSoftware = tk.Menu(menubar, tearoff=0)
            settingsMenuSoftware.add_command(
                label="Update",
                command=lambda: self.AppModule.MainThreadManager.AwsService.downloadSoftwareUpdate())
            menubar.add_cascade(label="Software", menu=settingsMenuSoftware)

        settingsMenuReaders = tk.Menu(menubar, tearoff=0)
        settingsMenuReaders.add_command(label="Frequency Range", command=lambda: self.Settings.freqRangeSetting())
        settingsMenuReaders.add_command(label="Scan Rate", command=lambda: self.Settings.rateSetting())
        settingsMenuReaders.add_command(label="File Save", command=lambda: self.Settings.saveFilesSetting())
        menubar.add_cascade(label="Readers", menu=settingsMenuReaders)

        settingsMenuAnalysis = tk.Menu(menubar, tearoff=0)
        settingsMenuAnalysis.add_command(label="Noise Reduction", command=lambda: self.Settings.denoiseSetting())
        settingsMenuAnalysis.add_command(label="Weak Signal Turn Off",
                                         command=lambda: self.Settings.weakSignalToggleSetting())
        menubar.add_cascade(label="Analysis", menu=settingsMenuAnalysis)

        settingsMenuDisplay = tk.Menu(menubar, tearoff=0)
        settingsMenuDisplay.add_command(label="SGI", command=lambda: self.Settings.freqToggleSetting("SGI"))
        settingsMenuDisplay.add_command(label="Signal Check",
                                        command=lambda: self.Settings.freqToggleSetting("Signal Check"))
        menubar.add_cascade(label="Display", menu=settingsMenuDisplay)

        return menubar

    def createTheme(self):
        self.RootManager.setTitle("Skroot Reader GUI")
        style = ttk.Style()
        style.theme_use('clam')
        self.RootManager.setBackgroundColor(self.Colors.secondaryColor)
        style.configure(
            'W.TButton',
            font=('Courier', 9, 'bold'),
            foreground=self.Colors.secondaryColor,
            background=self.Colors.primaryColor)
        style.map(
            'W.TButton',
            background=[("disabled", "gray23"), ("active", self.Colors.primaryColor)])

    def createFrames(self):
        footer = self.FrameManager.createFooterFrame()
        versionLabel = tk.Label(footer, text=f'Version: v{self.AppModule.version}', bg='white')
        versionLabel.place(relx=0.0, rely=1.0, anchor='sw')
        copyrightLabel = tk.Label(
            footer,
            text='\u00A9 Skroot Laboratory, Inc 2018-2024. All rights reserved.',
            bg='white')
        copyrightLabel.place(relx=0.5, rely=1.0, anchor='s')

        bodyFrame = self.FrameManager.createBodyFrame()
        bodyFrame.place(
            relx=0,
            rely=self.GuiProperties.bannerHeight,
            relwidth=1,
            relheight=self.GuiProperties.mainHeight)

        textFrame = self.FrameManager.createBannerFrame()
        text_notification.createWidget(textFrame)
        text_notification.setText("Skroot Laboratory - Follow the prompts to get started.")
        text_notification.packWidget()
        return bodyFrame
