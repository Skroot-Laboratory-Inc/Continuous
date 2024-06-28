import tkinter as tk
import tkinter.ttk as ttk

from src.app.widget import text_notification


class Setup:
    def __init__(self, root, Settings, AppModule):
        self.root = root
        self.Settings = Settings
        self.AppModule = AppModule
        self.createTheme()
        self.createFrames()

    def createMenus(self):
        self.AppModule.awsCheckSoftwareUpdates()
        menubar = tk.Menu(self.root)
        if self.AppModule.SoftwareUpdate.newestZipVersion:
            settingsMenuSoftware = tk.Menu(menubar, tearoff=0)
            settingsMenuSoftware.add_command(label="Update", command=lambda: self.AppModule.downloadSoftwareUpdate())
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
        self.root.title("Skroot Reader GUI")
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(background='white')
        style.configure('W.TButton', font=('Courier', 9, 'bold'), foreground=self.AppModule.secondaryColor,
                        background=self.AppModule.primaryColor)
        style.map('W.TButton', background=[("disabled", "gray23"), ("active", self.AppModule.primaryColor)])

    def createFrames(self):
        self.AppModule.readerPlotFrame = tk.Frame(self.root, bg=self.AppModule.secondaryColor)
        self.AppModule.readerPlotFrame.place(relx=0, rely=0.05, relwidth=1, relheight=0.92)
        footer = tk.Frame(self.root, bg=self.AppModule.secondaryColor)
        footer.place(relx=0, rely=0.97, relwidth=1, relheight=0.03)
        versionLabel = tk.Label(footer, text=f'Version: v{self.AppModule.version}', bg='white')
        versionLabel.place(relx=0.0, rely=1.0, anchor='sw')
        copyrightLabel = tk.Label(footer, text='\u00A9 Skroot Laboratory, Inc 2018-2024. All rights reserved.', bg='white')
        copyrightLabel.place(relx=0.5, rely=1.0, anchor='s')

        textFrame = tk.Frame(self.root, bg=self.AppModule.secondaryColor)
        text_notification.createWidget(textFrame)
        text_notification.setText("Skroot Laboratory - Follow the prompts to get started.")
        textFrame.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        text_notification.packWidget()
