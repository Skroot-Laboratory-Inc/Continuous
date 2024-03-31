import tkinter as tk
import tkinter.ttk as ttk

import text_notification


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
        settingsMenuAnalysis.add_command(label="Spline Analysis", command=lambda: self.Settings.splineToggleSetting())
        settingsMenuAnalysis.add_command(label="Email Notification", command=lambda: self.Settings.foamEmailSetting())
        settingsMenuAnalysis.add_command(label="Foaming Threshold", command=lambda: self.Settings.foamThreshSetting())
        menubar.add_cascade(label="Analysis", menu=settingsMenuAnalysis)

        settingsMenuDisplay = tk.Menu(menubar, tearoff=0)
        settingsMenuDisplay.add_command(label="SGI", command=lambda: self.Settings.freqToggleSetting("SGI"))
        settingsMenuDisplay.add_command(label="Signal Strength",
                                        command=lambda: self.Settings.freqToggleSetting("Signal Strength"))
        settingsMenuDisplay.add_command(label="Signal Check",
                                        command=lambda: self.Settings.freqToggleSetting("Signal Check"))
        menubar.add_cascade(label="Display", menu=settingsMenuDisplay)

        return menubar

    def createTheme(self):
        self.root.title("Skroot Reader GUI")
        height = self.root.winfo_screenheight()  # 800 # height of the window
        width = self.root.winfo_screenwidth()  # 1200 # width of the window
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('W.TButton', font=('Courier', 9, 'bold'), foreground=self.AppModule.white,
                        background=self.AppModule.royalBlue)
        style.map('W.TButton', background=[("disabled", "gray23"), ("active", "royal blue")])
        style.map('TMenuButton', background=[("disabled", "gray23"), ("active", "royal blue")])
        canvas = tk.Canvas(self.root, height=height, width=width)
        canvas.pack()
        self.AppModule.royalBlue = 'RoyalBlue4'
        self.AppModule.white = 'white'

    def createFrames(self):
        self.AppModule.readerPlotFrame = tk.Frame(self.root, bg=self.AppModule.white)
        self.AppModule.readerPlotFrame.place(relx=0, rely=0.05, relwidth=1, relheight=0.95)
        versionLabel = tk.Label(self.AppModule.readerPlotFrame, text=f'Version: v{self.AppModule.version}', bg='white')
        versionLabel.place(relx=0.0, rely=1.0, anchor='sw')

        textFrame = tk.Frame(self.root, bg=self.AppModule.white)
        text_notification.createWidget(textFrame)
        text_notification.setText("Skroot Laboratory - Follow the prompts to get started.")
        textFrame.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        text_notification.packWidget()
