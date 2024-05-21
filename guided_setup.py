import os
import tkinter as tk
import tkinter.ttk as ttk
import pyautogui


def guidedSetupCell(root, baseSavePath, month, day, year, numReaders, scanRate, cellType, secondAxisTitle, equilibrationTime):
    setupForm = SetupForm(root, baseSavePath, month, day, year, numReaders, scanRate, cellType,
                          secondAxisTitle, equilibrationTime)
    month, day, year, savePath, numReaders, scanRate, calibrate, secondAxisTitle, cellType, equilibrationTime = setupForm.getConfiguration()
    return month, day, year, savePath, numReaders, scanRate, calibrate, cellType, secondAxisTitle, equilibrationTime


def guidedSetupFoaming(root, baseSavePath, month, day, year, numReaders, scanRate, cellType):
    # TODO - update this to account for foaming setup, it will be different values needed
    setupForm = SetupForm(root, baseSavePath, month, day, year, numReaders, scanRate, cellType, "")
    month, day, year, savePath, numReaders, scanRate, calibrate, secondAxisTitle, cellType = setupForm.getConfiguration()
    return savePath, numReaders, scanRate, calibrate, secondAxisTitle


class SetupForm:
    def __init__(self, root, baseSavePath, month, day, year, numReaders, scanRate, cellType,
                 secondAxisTitle, equilibrationTime):
        self.secondAxisTitle = ""
        self.cellType = None
        self.year = None
        self.month = None
        self.day = None
        self.baseSavePath = baseSavePath
        self.scanRate = None
        self.savePath = None
        self.numReaders = None
        self.equilibrationTime = None
        self.calibrate = True
        self.secondAxis = False
        self.entrySize = 10
        self.calibrateRequired = tk.IntVar(value=1)
        self.equilibrationTimeEntry = tk.StringVar(value=equilibrationTime)
        self.secondAxisEntry = tk.StringVar(value=secondAxisTitle)
        self.cellTypeEntry = tk.StringVar(value=cellType)
        self.monthEntry = tk.IntVar(value=month)
        self.dayEntry = tk.IntVar(value=day)
        self.yearEntry = tk.IntVar(value=year)
        self.numReadersEntry = tk.StringVar(value=numReaders)
        self.scanRateEntry = tk.StringVar(value=scanRate)
        self.window = tk.Toplevel(root, bg='white', padx=25, pady=25)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.minsize(200, 200)
        self.window.protocol("WM_DELETE_WINDOW", self.onSubmit)
        w = self.window.winfo_reqwidth()
        h = self.window.winfo_reqheight()
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.window.geometry('+%d+%d' % (x, y))
        self.window.tkraise(root)

        ''' MM DD YYYY Date entry '''
        dateFrame = tk.Frame(self.window, bg='white')
        tk.Spinbox(dateFrame, textvariable=self.monthEntry, width=round(self.entrySize / 4), from_=1, to=12,
                   borderwidth=0, highlightthickness=0).grid(row=0, column=1)
        tk.Label(dateFrame, text="/", bg='white', width=round(self.entrySize / 10)).grid(row=0, column=2)
        tk.Spinbox(dateFrame, textvariable=self.dayEntry, width=round(self.entrySize / 4), from_=1, to=31,
                   borderwidth=0, highlightthickness=0).grid(row=0, column=3)
        tk.Label(dateFrame, text="/", bg='white', width=round(self.entrySize / 10)).grid(row=0, column=4)
        tk.Spinbox(dateFrame, textvariable=self.yearEntry, width=round(self.entrySize / 2), from_=2023, to=2050,
                   borderwidth=0, highlightthickness=0).grid(row=0, column=5)

        ''' Normal entries '''
        entriesMap = {}
        row = 0

        entriesMap['Date'] = dateFrame

        entriesMap['Cell Type'] = tk.Entry(self.window, textvariable=self.cellTypeEntry, borderwidth=0, highlightthickness=0, justify="center")

        options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        entriesMap["Number of Readers"] = createDropdown(self.window, self.numReadersEntry, options, True)

        options = ["2", "5", "10"]
        entriesMap["Scan Rate (min)"] = createDropdown(self.window, self.scanRateEntry, options, True)

        options = ["0", "2", "12", "24"]
        entriesMap["Equilibration Time (hr)"] = createDropdown(self.window, self.equilibrationTimeEntry, options, True)

        options = ["", "Glucose", "Lactate", "Optical Density", "Cell Count"]
        entriesMap["Additional User Input"] = createDropdown(self.window, self.secondAxisEntry, options, False)

        ''' Create Label and Entry Widgets'''
        for entryLabelText, entry in entriesMap.items():
            tk.Label(self.window, text=entryLabelText, bg='white').grid(row=row, column=0, sticky='w')
            entry.grid(row=row, column=1, sticky="ew")
            row += 1
            ttk.Separator(self.window, orient="horizontal").grid(row=row, column=1, sticky="ew")
            row += 1

        ''' Create Spacer between entries and submit option '''
        spacer = tk.Entry(self.window, borderwidth=0, highlightthickness=0, disabledbackground="white", cursor='arrow')
        row += 1
        spacer.grid(row=row, column=1, sticky="ew")
        spacer['state'] = "disabled"

        var = tk.Checkbutton(self.window, text="Calibration Required", variable=self.calibrateRequired, onvalue=1, offvalue=0,
                       command=self.setCalibrate, bg='white', borderwidth=0, highlightthickness=0)
        var.grid(row=row, column=1, sticky="ew")

        self.submitButton = ttk.Button(self.window, text="Submit", command=lambda: self.onSubmit())
        row += 1
        self.submitButton.grid(row=row, column=0, sticky="sw")
        self.submitButton['style'] = 'W.TButton'
        root.wait_window(self.window)

    def getConfiguration(self):
        return self.month, self.day, self.year, self.savePath, self.numReaders, self.scanRate, self.calibrate, self.secondAxisTitle, self.cellType, self.equilibrationTime

    def setCalibrate(self):
        if self.calibrateRequired.get() == 1:
            self.calibrate = True
        if self.calibrateRequired.get() == 0:
            self.calibrate = False

    def onSubmit(self):
        if (self.monthEntry.get() != "" and self.dayEntry.get() != "" and self.yearEntry.get() != "" and self.cellTypeEntry.get() != ""):
            date = f"{self.monthEntry.get()}-{self.dayEntry.get()}-{self.yearEntry.get()}"
            self.numReaders = int(self.numReadersEntry.get())
            self.equilibrationTime = int(self.equilibrationTimeEntry.get())
            self.scanRate = float(self.scanRateEntry.get())
            if not os.path.exists(
                    f"{self.baseSavePath}/{date}_{self.cellTypeEntry.get()}"):
                self.savePath = f"{self.baseSavePath}/{date}_{self.cellTypeEntry.get()}"
            else:
                incrementalNumber = 0
                while os.path.exists(
                        f"{self.baseSavePath}/{date}_{self.cellTypeEntry.get()} ({incrementalNumber})"):
                    incrementalNumber += 1
                self.savePath = f"{self.baseSavePath}/{date}_{self.cellTypeEntry.get()} ({incrementalNumber})"
            self.month, self.day, self.year, self.cellType, self.secondAxisTitle = self.monthEntry.get(), self.dayEntry.get(), self.yearEntry.get(), self.cellTypeEntry.get(), self.secondAxisEntry.get()
            self.takeScreenshot()
            self.window.destroy()
        else:
            tk.messagebox.showerror("Incorrect Formatting", "One (or more) of the values entered is not formatted "
                                                            "properly")
            self.window.tkraise()

    def takeScreenshot(self):
        x, y = self.window.winfo_rootx(), self.window.winfo_rooty()
        w, h = self.window.winfo_width(), self.window.winfo_height()
        if not os.path.exists(os.path.dirname(self.savePath)):
            os.mkdir(os.path.dirname(self.savePath))
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)
        im = pyautogui.screenshot(region=(x, y, w, round(h * 0.77)))
        im.save(f'{self.savePath}/setupForm.png')


def createDropdown(root, entryVariable, options, addSpace):
    if addSpace:
        options = [f"             {option}             " for option in options]
    scanRateValue = entryVariable.get()
    optionMenu = tk.OptionMenu(root, entryVariable, *options)
    optionMenu.config(bg="white", borderwidth=0, highlightthickness=0, indicatoron=False)
    optionMenu["menu"].config(bg="white")
    entryVariable.set(scanRateValue)
    return optionMenu
