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
        settingsMenuReaders.add_command(label="Number of readers", command=lambda: self.Settings.setNumReaders())
        settingsMenuReaders.add_command(label="Frequency Range", command=lambda: self.Settings.freqRangeSetting())
        settingsMenuReaders.add_command(label="Number of points", command=lambda: self.Settings.nPointsSetting())
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

    def createFramesAndButtons(self):
        rightFrame = tk.Frame(self.root, bg=self.AppModule.royalBlue)  # consider this a div, border = 5
        textFrame = tk.Frame(rightFrame, bg=self.AppModule.royalBlue)
        outerFrame = tk.Frame(self.root, bg=self.AppModule.white)
        text_notification.createWidget(textFrame)
        text_notification.setText("")

        outerFrame.place(relx=0, rely=0, relwidth=0.7, relheight=1)
        rightFrame.place(relx=0.7, rely=0, relwidth=0.3, relheight=1)
        textFrame.place(rely=0, relx=0.15, relwidth=0.7, relheight=0.09)
        text_notification.packWidget()

        self.AppModule.browseButton = ttk.Button(rightFrame, text="Browse", command=lambda: self.Buttons.browseFunc())
        self.AppModule.startButton = ttk.Button(rightFrame, text="Start", command=lambda: self.Buttons.startFunc())
        self.AppModule.stopButton = ttk.Button(rightFrame, text="Stop", command=lambda: self.Buttons.stopFunc())
        airFreqLabel = ttk.Label(rightFrame, text="Air Frequency (MHz)", borderwidth=0)
        self.AppModule.airFreqInput = ttk.Entry(rightFrame)
        waterFreqLabel = ttk.Label(rightFrame, text="Liquid Frequency (MHz)", borderwidth=0)
        self.AppModule.waterFreqInput = ttk.Entry(rightFrame)
        self.AppModule.submitButton = ttk.Button(rightFrame, text="Submit", command=lambda: self.Buttons.submitFunc())

        # Placing the items on the GUI
        buttonInitialY = 0.09
        spacingY = 0.06
        xPadding = 0.15
        buttonWidth = 1 - xPadding * 2
        buttonHeight = 0.05
        textHeight = 0.03
        order = [self.AppModule.browseButton,
                 self.AppModule.startButton,
                 self.AppModule.stopButton,
                 airFreqLabel,
                 self.AppModule.airFreqInput,
                 waterFreqLabel,
                 self.AppModule.waterFreqInput,
                 self.AppModule.submitButton]

        currentY = buttonInitialY
        for i in range(len(order)):
            if isinstance(order[i], ttk.Button):
                if i != 0:
                    currentY += spacingY
                order[i].place(rely=currentY, relx=xPadding, relwidth=buttonWidth, relheight=buttonHeight)
            elif isinstance(order[i], ttk.Label) and isinstance(order[i - 1], ttk.Entry):
                if i != 0:
                    currentY += (spacingY - textHeight)
                order[i].place(rely=currentY, relx=xPadding, relwidth=buttonWidth, relheight=textHeight)
            elif isinstance(order[i], ttk.Label):
                if i != 0:
                    currentY += spacingY
                order[i].place(rely=currentY, relx=xPadding, relwidth=buttonWidth, relheight=textHeight)
            elif isinstance(order[i], ttk.Entry) and isinstance(order[i - 1], ttk.Label):
                if i != 0:
                    currentY += (spacingY - textHeight)
                order[i].place(rely=currentY, relx=xPadding, relwidth=buttonWidth, relheight=textHeight)
            elif isinstance(order[i], ttk.Entry):
                if i != 0:
                    currentY += textHeight
                order[i].place(rely=currentY, relx=xPadding, relwidth=buttonWidth, relheight=textHeight)
        self.AppModule.summaryFrame = tk.Frame(rightFrame, bg=self.AppModule.white, bd=0)
        self.AppModule.summaryFrame.place(anchor='n', rely=(currentY + spacingY), relx=0.5, relwidth=1,
                                          relheight=1 - (currentY + spacingY))

        # Other buttons that will be invoked
        self.AppModule.summaryPlotButton = ttk.Button(rightFrame, text="Summary Plot Update",
                                                      command=lambda: self.AppModule.plotSummary())

        buttons = [self.AppModule.browseButton, self.AppModule.submitButton, self.AppModule.startButton,
                   self.AppModule.stopButton, self.AppModule.summaryPlotButton]
        for b in buttons:
            b['state'] = 'disabled'
            b['style'] = 'W.TButton'
        airFreqLabel['style'] = 'W.TButton'
        waterFreqLabel['style'] = 'W.TButton'
        self.AppModule.submitButton['state'] = 'normal'
        self.AppModule.browseButton['state'] = 'normal'
