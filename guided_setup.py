from __future__ import print_function

import os
import tkinter as tk
import tkinter.ttk as ttk


def guidedSetupCell(root, baseSavePath, month, day, year, numReaders, scanRate, cellType, vesselType, secondAxisTitle):
    setupForm = SetupForm(root, baseSavePath, month, day, year, numReaders, scanRate, cellType, vesselType, secondAxisTitle)
    month, day, year, savePath, numReaders, scanRate, calibrate, secondAxisTitle, cellType, vesselType = setupForm.getConfiguration()
    # second_win.withdraw()
    # logger.info("skipped")
    # savePath = setSavePath(second_win, baseSavePath)
    # numReaders = askNumReaders(second_win)
    # numReaders = int(numReaders)
    # scanRate = askScanRate(second_win)
    # scanRate = scanRate
    # second_win.destroy()
    # calibrate = askCalibrateReaders()

    # maybeSecondaryAxis = askSecondaryAxis()
    # if maybeSecondaryAxis:
    #     secondAxisTitle = maybeSecondaryAxis
    # else:
    #     secondAxisTitle = ""
    return month, day, year, savePath, numReaders, scanRate, calibrate, secondAxisTitle, cellType, vesselType


def guidedSetupFoaming(root, baseSavePath, month, day, year, numReaders, scanRate, cellType, vesselType):
    setupForm = SetupForm(root, baseSavePath, month, day, year, numReaders, scanRate, cellType, vesselType)
    month, day, year, savePath, numReaders, scanRate, calibrate, secondAxisTitle, cellType, vesselType = setupForm.getConfiguration()
    # second_win.withdraw()
    # logger.info("skipped")
    # savePath = setSavePath(second_win, baseSavePath)
    # numReaders = askNumReaders(second_win)
    # numReaders = int(numReaders)
    # scanRate = askScanRate(second_win)
    # scanRate = scanRate
    # second_win.destroy()
    # calibrate = askCalibrateReaders()

    # maybeSecondaryAxis = askSecondaryAxis()
    # if maybeSecondaryAxis:
    #     secondAxisTitle = maybeSecondaryAxis
    # else:
    #     secondAxisTitle = ""
    return savePath, numReaders, scanRate, calibrate, secondAxisTitle


class SetupForm:
    def __init__(self, root, baseSavePath, month, day, year, numReaders, scanRate, cellType, vesselType, secondAxisTitle):
        self.secondAxisTitle = None
        self.vesselType = None
        self.cellType = None
        self.year = None
        self.month = None
        self.day = None
        self.baseSavePath = baseSavePath
        self.scanRate = None
        self.savePath = None
        self.numReaders = None
        self.calibrate = False
        self.secondAxis = False
        self.entrySize = 10
        self.calibrateRequired = tk.IntVar()
        self.secondAxisEntry = tk.StringVar(value=secondAxisTitle)
        self.cellTypeEntry = tk.StringVar(value=cellType)
        self.vesselTypeEntry = tk.StringVar(value=vesselType)
        self.monthEntry = tk.IntVar(value=month)
        self.dayEntry = tk.IntVar(value=day)
        self.yearEntry = tk.IntVar(value=year)
        self.numReadersEntry = tk.IntVar(value=numReaders)
        self.scanRateEntry = tk.StringVar(value=scanRate)
        self.window = tk.Toplevel(root, bg='white', padx=25, pady=25)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.minsize(200, 200)
        self.window.maxsize(200, 200)
        self.window.protocol("WM_DELETE_WINDOW", self.onSubmit)
        root.eval(f'tk::PlaceWindow {str(self.window)} center')
        tk.Label(self.window, text="Date", bg='white').grid(row=0, column=0, sticky='w')
        tk.Label(self.window, text="Cell Type", bg='white').grid(row=2, column=0, sticky='w')
        tk.Label(self.window, text="Vessel Type", bg='white').grid(row=4, column=0, sticky='w')
        tk.Label(self.window, text="Number of Readers", bg='white').grid(row=6, column=0, sticky='w')
        tk.Label(self.window, text="Scan Rate", bg='white').grid(row=8, column=0, sticky='w')
        tk.Label(self.window, text="Second Axis (optional)", bg='white').grid(row=10, column=0, sticky='w')

        dateFrame = tk.Frame(self.window, bg='white')
        tk.Spinbox(dateFrame, textvariable=self.monthEntry, width=round(self.entrySize / 4), from_=1, to=12, borderwidth=0, highlightthickness=0).grid(row=0, column=1)
        tk.Label(dateFrame, text="/", bg='white', width=round(self.entrySize / 10)).grid(row=0, column=2)
        tk.Spinbox(dateFrame, textvariable=self.dayEntry, width=round(self.entrySize / 4), from_=1, to=31, borderwidth=0, highlightthickness=0).grid(row=0, column=3)
        tk.Label(dateFrame, text="/", bg='white', width=round(self.entrySize / 10)).grid(row=0, column=4)
        tk.Spinbox(dateFrame, textvariable=self.yearEntry, width=round(self.entrySize / 2), from_=2023, to=2050, borderwidth=0, highlightthickness=0).grid(row=0, column=5)
        dateFrame.grid(row=0, column=1, sticky="ew")
        ttk.Separator(self.window, orient="horizontal").grid(row=1, column=1, sticky="ew")

        tk.Entry(self.window, textvariable=self.cellTypeEntry, borderwidth=0, highlightthickness=0).grid(row=2, column=1, sticky="ew")
        ttk.Separator(self.window, orient="horizontal").grid(row=3, column=1, sticky="ew")

        tk.Entry(self.window, textvariable=self.vesselTypeEntry, borderwidth=0, highlightthickness=0).grid(row=4, column=1, sticky="ew")
        ttk.Separator(self.window, orient="horizontal").grid(row=5, column=1, sticky="ew")

        tk.Spinbox(self.window, textvariable=self.numReadersEntry, from_=1, to=12, wrap=True, borderwidth=0, highlightthickness=0).grid(row=6, column=1, sticky="ew")
        ttk.Separator(self.window, orient="horizontal").grid(row=7, column=1, sticky="ew")

        tk.Spinbox(self.window, textvariable=self.scanRateEntry, values=("0.5", "1", "2", "3", "5", "10"), wrap=True, borderwidth=0, highlightthickness=0).grid(row=8, column=1, sticky="ew")
        ttk.Separator(self.window, orient="horizontal").grid(row=9, column=1, sticky="ew")

        tk.Entry(self.window, textvariable=self.secondAxisEntry, borderwidth=0, highlightthickness=0).grid(row=10, column=1, sticky="ew")
        ttk.Separator(self.window, orient="horizontal").grid(row=11, column=1, sticky="ew")

        spacer = tk.Entry(self.window, borderwidth=0, highlightthickness=0, disabledbackground="white", cursor='arrow')
        spacer.grid(row=12, column=1, sticky="ew")
        spacer['state'] = "disabled"

        tk.Checkbutton(self.window, text="Calibration Required", variable=self.calibrateRequired, onvalue=1, offvalue=0,
                       command=self.setCalibrate, bg='white', borderwidth=0, highlightthickness=0).grid(row=13, column=1, sticky="ew")

        self.submitButton = ttk.Button(self.window, text="Submit", command=lambda: self.onSubmit())
        self.submitButton.grid(row=13, column=0, sticky="sw")
        self.submitButton['style'] = 'W.TButton'
        root.wait_window(self.window)

    def getConfiguration(self):
        return self.month, self.day, self.year, self.savePath, self.numReaders, self.scanRate, self.calibrate, self.cellType, self.vesselType, self.secondAxisTitle

    def setCalibrate(self):
        if self.calibrateRequired.get() == 1:
            self.calibrate = True
        if self.calibrateRequired.get() == 0:
            self.calibrate = False

    def onSubmit(self):
        if (self.monthEntry.get() != "" and self.dayEntry.get() != "" and self.yearEntry.get() != ""
                and self.numReadersEntry.get() != "" and self.scanRateEntry.get() != ""
                and self.vesselTypeEntry.get() != "" and self.cellTypeEntry.get() != ""):
            date = f"{self.monthEntry.get()}-{self.dayEntry.get()}-{self.yearEntry.get()}"
            self.numReaders = int(self.numReadersEntry.get())
            self.scanRate = float(self.scanRateEntry.get())
            if not os.path.exists(
                    f"{self.baseSavePath}/{date}_{self.cellTypeEntry.get()}_{self.vesselTypeEntry.get()}"):
                self.savePath = f"{self.baseSavePath}/{date}_{self.cellTypeEntry.get()}_{self.vesselTypeEntry.get()}"
            else:
                incrementalNumber = 0
                while os.path.exists(
                        f"{self.baseSavePath}/{date}_{self.cellTypeEntry.get()}_{self.vesselTypeEntry.get()} ({incrementalNumber})"):
                    incrementalNumber += 1
                self.savePath = f"{self.baseSavePath}/{date}_{self.cellTypeEntry.get()}_{self.vesselTypeEntry.get()} ({incrementalNumber})"
            self.month, self.day, self.year, self.vesselType, self.cellType, self.secondAxisTitle = self.monthEntry.get(), self.dayEntry.get(), self.yearEntry.get(), self.vesselTypeEntry.get(), self.cellTypeEntry.get(), self.secondAxisEntry.get()
            self.window.destroy()
        else:
            tk.messagebox.showerror("Incorrect Formatting", "One (or more) of the values entered is not formatted "
                                                            "properly")
            self.window.tkraise()


def setSavePath(second_win, baseSavePath):
    date = askDate(second_win)
    cellType = askCellType(second_win)
    vesselType = askVesselType(second_win)
    if not os.path.exists(f"{baseSavePath}/{date}_{cellType}_{vesselType}"):
        return f"{baseSavePath}/{date}_{cellType}_{vesselType}"
    else:
        incrementalNumber = 0
        while os.path.exists(f"{baseSavePath}/{date}_{cellType}_{vesselType} ({incrementalNumber})"):
            incrementalNumber += 1
        return f"{baseSavePath}/{date}_{cellType}_{vesselType} ({incrementalNumber})"


def askDate(root):
    date = ''
    formattedWrong = False
    while date == '':
        if not formattedWrong:
            dateRaw = tk.simpledialog.askstring(f"Today's Date", "Enter today's date (MM/DD/YYYY)", parent=root)
        else:
            dateRaw = tk.simpledialog.askstring(f"Check Formatting", "Check the formatting - Enter today's date ("
                                                                     "MM/DD/YYYY)", parent=root)
        try:
            dateList = dateRaw.split("/")
            print(dateList)
            if len(dateList) < 3:
                formattedWrong = True
                continue
            if int(dateList[0]) > 12:
                formattedWrong = True
                continue
            if int(dateList[1]) > 31:
                formattedWrong = True
                continue
            if int(dateList[2]) < 2023:
                formattedWrong = True
                continue
            date = f"{dateList[0]}-{dateList[1]}-{dateList[2]}"
        except:
            formattedWrong = True
            continue
    return date


def setDate(AppModule, result):
    AppModule.date = result


def askVesselType(root):
    vessel = None
    while vessel is None:
        vessel = tk.simpledialog.askstring(f"Vessel Type", "Enter the vessel you are using", parent=root)
    return vessel


def askCellType(root):
    cell = None
    while cell is None:
        cell = tk.simpledialog.askstring(f"Cell Type", "Enter the cells you are growing.", parent=root)
    return cell


def askNumReaders(root):
    numReaders = ''
    while numReaders == "":
        numReaders = tk.simpledialog.askinteger("Input", "Number of readers used: \nRange: (1 - 12)", parent=root,
                                                minvalue=1, maxvalue=12)
    return numReaders


def askScanRate(root):
    scanRate = ''
    while scanRate == '':
        scanRate = tk.simpledialog.askfloat("Scan Rate", "Scan Rate (minutes between scans): \nRange: (0.1 - 10)",
                                            parent=root, minvalue=0.1, maxvalue=10.0)
    return scanRate


def askCalibrateReaders():
    calibrate = None
    while calibrate is None:
        calibrate = tk.messagebox.askyesno("Calibration", "Do you need to calibrate the readers?")
    return calibrate


def askSecondaryAxis():
    useSecondAxis = tk.messagebox.askyesno("Secondary Axis", "Would you like to plot anything against the results?")
    if useSecondAxis:
        return tk.simpledialog.askstring("Second Axis", "What would you like to plot against?")
    else:
        return False


def askIfFoamCalibrated():
    maybeFoamCalibrated = tk.messagebox.askyesno("Secondary Axis",
                                                 "Would you like to plot anything against the results?")
    if maybeFoamCalibrated:
        return tk.simpledialog.askstring("What would you like to plot against?")
    else:
        return False


def askAirFreq():
    airFreq = tk.messagebox.askyesno("Secondary Axis", "Would you like to plot anything against the results?")
    if airFreq:
        return tk.simpledialog.askstring("What would you like to plot against?")
    else:
        return False


def askWaterFreq():
    waterFreq = tk.messagebox.askyesno("Secondary Axis", "Would you like to plot anything against the results?")
    if waterFreq:
        return tk.simpledialog.askstring("What would you like to plot against?")
    else:
        return False
