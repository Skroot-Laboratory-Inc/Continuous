import tkinter as tk
import tkinter.ttk as ttk

import text_notification


class Setup:
    def __init__(self, root, Buttons, Settings, AppModule):
        self.root = root
        self.Buttons = Buttons
        self.Settings = Settings
        self.AppModule = AppModule

    def createMenus(self):
        menubar = tk.Menu(self.root)
        settingsMenuReaders = tk.Menu(menubar, tearoff=0)
        settingsMenuReaders.add_command(label="Frequency Range", command=lambda: self.Settings.freqRangeSetting())
        settingsMenuReaders.add_command(label="Scan Rate", command=lambda: self.Settings.rateSetting())
        settingsMenuReaders.add_command(label="File Save", command=lambda: self.Settings.saveFilesSetting())
        settingsMenuReaders.add_command(label="Calibrate", command=lambda: self.Buttons.calFunc())
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
        settingsMenuDisplay.add_command(label="Frequency", command=lambda: self.Settings.freqToggleSetting("Frequency"))
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
        style.configure('W.TButton', font=('Courier', 9, 'bold'), foreground="white", background="RoyalBlue4")
        style.map('W.TButton', background=[("disabled", "gray23"), ("active", "royal blue")])
        canvas = tk.Canvas(self.root, height=height, width=width)
        canvas.pack()
        self.AppModule.royalBlue = 'RoyalBlue4'
        self.AppModule.white = 'white'

    def createFrames(self):
        spaceForPlots = 0.9
        self.AppModule.readerPlotFrame = tk.Frame(self.root, bg=self.AppModule.white)
        self.AppModule.readerPlotFrame.place(relx=0, rely=0.05, relwidth=1, relheight=0.95)

        textFrame = tk.Frame(self.root, bg=self.AppModule.white)
        text_notification.createWidget(textFrame)
        text_notification.setText("Skroot Laboratory - Follow the prompts to get started.")
        textFrame.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        text_notification.packWidget()

        self.AppModule.summaryFrame = tk.Frame(self.AppModule.readerPlotFrame, bg=self.AppModule.white, bd=0)
        self.AppModule.summaryFrame.place(rely=0.5*spaceForPlots, relx=0.67, relwidth=0.3, relheight=0.45*spaceForPlots)

        # Other buttons that will be invoked
        self.AppModule.summaryPlotButton = ttk.Button(self.AppModule.readerPlotFrame, text="Summary Plot Update",
                                                      command=lambda: self.AppModule.plotSummary())
