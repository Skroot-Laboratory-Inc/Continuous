import tkinter as tk
import tkinter.ttk as ttk

from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.common_modules.initialization.frame_manager import FrameManager
from src.app.common_modules.service.dev_software_update import DevSoftwareUpdate
from src.app.common_modules.service.software_update import SoftwareUpdate
from src.app.properties.dev_properties import DevProperties
from src.app.ui_manager.buttons.connectivity_button import ConnectivityButton
from src.app.ui_manager.buttons.power_button import PowerButton
from src.app.ui_manager.buttons.profile_button import ProfileButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.theme.gui_properties import GuiProperties
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget import text_notification
from src.app.widget.sidebar.helpers.functions import hasValidAwsCredentials
from src.app.widget.sidebar.sidebar import Sidebar


class SetupBaseUi:
    def __init__(self, rootManager: RootManager, sessionManager: SessionManager, major_version, minor_version):

        self.RootManager = rootManager
        self.SessionManager = sessionManager
        self.isDevMode = DevProperties().isDevMode
        if self.isDevMode:
            self.SoftwareUpdate = DevSoftwareUpdate(self.RootManager, major_version, minor_version)
        else:
            self.SoftwareUpdate = SoftwareUpdate(self.RootManager, major_version, minor_version)
        self.FrameManager = FrameManager(self.RootManager)
        self.GuiProperties = GuiProperties()
        self.version = f'{major_version}.{minor_version}'
        self.isDevMode = DevProperties().isDevMode

        # Check AWS credentials at startup (cached forever)
        hasValidAwsCredentials()

        self.bodyFrame, self.sidebar = self.createFrames()
        self.createTheme()

    def createFrames(self):
        self.FrameManager.footerFrame.grid_columnconfigure(0, weight=0)
        self.FrameManager.footerFrame.grid_columnconfigure(1, weight=1)
        self.FrameManager.footerFrame.grid_columnconfigure(2, weight=0)
        versionLabel = tk.Label(self.FrameManager.footerFrame, text=f'v{self.version}', bg=Colors().body.background, fg=Colors().body.text)
        versionLabel.grid(row=0, column=0, sticky="sw")
        copyrightLabel = tk.Label(
            self.FrameManager.footerFrame,
            text='\u00A9 Skroot Laboratory, Inc 2018-2025. All rights reserved.',
            bg=Colors().body.background, fg=Colors().body.text)
        copyrightLabel.grid(row=0, column=1, sticky="s")
        poweredByLabel = tk.Label(
            self.FrameManager.footerFrame,
            text='Powered by Skroot',
            bg=Colors().body.background, fg=Colors().body.text)
        poweredByLabel.grid(row=0, column=2, sticky="se")

        self.FrameManager.bannerFrame.grid_rowconfigure(0, weight=1)
        self.FrameManager.bannerFrame.grid_columnconfigure(0, weight=0)
        self.FrameManager.bannerFrame.grid_columnconfigure(1, weight=1)
        self.FrameManager.bannerFrame.grid_columnconfigure(2, weight=0)
        self.FrameManager.bannerFrame.grid_columnconfigure(3, weight=0)
        self.FrameManager.bannerFrame.grid_columnconfigure(4, weight=0)
        text_notification.createWidget(self.FrameManager.bannerFrame)
        text_notification.setText("Press the '+' icon to start a run.")
        text_notification.getWidget().grid(row=0, column=1, sticky="nsew")
        profileButton = ProfileButton(self.FrameManager.bannerFrame, self.RootManager, self.SessionManager).button
        profileButton.grid(row=0, column=2, sticky='nsew')
        self.RootManager.popupDisplayed.subscribe(lambda toggle: toggleButton(toggle, profileButton))
        connectivityButtonInstance = ConnectivityButton(self.FrameManager.bannerFrame, self.RootManager)
        connectivityButtonInstance.button.grid(row=0, column=3, sticky='nse')
        self.RootManager.popupDisplayed.subscribe(lambda toggle: toggleButton(toggle, connectivityButtonInstance.button))
        powerButton = PowerButton(self.FrameManager.bannerFrame, self.RootManager, self.SessionManager).button
        powerButton.grid(row=0, column=4, sticky='nse')
        self.RootManager.popupDisplayed.subscribe(lambda toggle: toggleButton(toggle, powerButton))
        sidebar = Sidebar(self.RootManager, self.SessionManager, self.FrameManager.bodyFrame, self.FrameManager.bannerFrame, self.SoftwareUpdate, connectivityButtonInstance)
        sidebar.getHamburger.grid(row=0, column=0, sticky='nsw')
        self.RootManager.popupDisplayed.subscribe(lambda toggle: toggleButton(toggle, sidebar.getHamburger))
        return self.FrameManager.bodyFrame, sidebar

    def createTheme(self):
        self.RootManager.setTitle("Skroot Reader GUI")
        style = ttk.Style()
        style.theme_use('clam')
        self.RootManager.setBackgroundColor(Colors().body.background)

        style.configure("Custom.Horizontal.TProgressbar",
                        background=Colors().buttons.background,
                        troughground=Colors().body.background,
                        )

        style.configure(
            'Default.TButton',
            font=FontTheme().buttons,
            padding=WidgetTheme().defaultButtonPadding,
            foreground=Colors().body.background,
            background=Colors().buttons.background)

        style.configure(
            'Toggle.TButton',
            font=('Helvetica', 60, 'bold'),
            padding=(0, 0),
            borderwidth=0,
            width=2,
            highlightthickness=0,
            foreground=Colors().buttons.background,
            background=Colors().body.background)

        style.configure(
            'Start.TButton',
            font=FontTheme().buttons,
            padding=WidgetTheme().defaultButtonPadding,
            foreground=Colors().body.background,
            background=Colors().status.success)

        style.configure(
            'Stop.TButton',
            font=FontTheme().buttons,
            padding=WidgetTheme().defaultButtonPadding,
            foreground=Colors().body.background,
            background=Colors().status.error)

        style.configure(
            'Entry.TButton',
            font=FontTheme().buttons,
            padding=(15, 15),
            width=5,
            foreground=Colors().body.background,
            background=Colors().buttons.background)
        style.configure(
            'Help.TButton',
            font=FontTheme().helpButton,
            foreground=Colors().body.background,
            background=Colors().buttons.background)
        style.configure(
            'Profile.TButton',
            focuscolor="none",
            highlightthickness=0,
            borderwidth=0,
            font=FontTheme().profileButton,
            foreground=Colors().header.text,
            disabledforeground=Colors().header.text,
            background=Colors().header.background)
        style.map(
            'Default.TButton',
            background=[("disabled", "gray23"), ("active", Colors().buttons.background)])
        style.map(
            'Start.TButton',
            background=[("disabled", "gray23"), ("active", Colors().status.success)])
        style.map(
            'Stop.TButton',
            background=[("disabled", "gray23"), ("active", Colors().status.error)])
        style.map(
            'Entry.TButton',
            background=[("disabled", "gray23"), ("active", Colors().buttons.background)])
        style.map(
            'Help.TButton',
            background=[("disabled", "gray23"), ("active", Colors().buttons.background)])
        style.map(
            'Toggle.TButton',
            background=[("disabled", "gray23"), ("active", Colors().body.background)])
        style.map(
            'Profile.TButton',
            background=[("disabled", Colors().header.background), ("active", Colors().header.background)],
            foreground=[("disabled", Colors().header.text), ("active", Colors().header.text)])


def toggleButton(toggle, button):
    button.grid_remove() if toggle else button.grid()