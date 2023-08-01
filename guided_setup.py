from __future__ import print_function

import os
import tkinter as tk


def guidedSetupCell(root, baseSavePath):
    second_win = tk.Toplevel(root)
    second_win.maxsize(1, 1)
    root.eval(f'tk::PlaceWindow {str(second_win)} center')
    second_win.withdraw()
    savePath = setSavePath(second_win, baseSavePath)
    numReaders = askNumReaders(second_win)
    numReaders = int(numReaders)
    scanRate = askScanRate(second_win)
    scanRate = scanRate
    second_win.destroy()
    calibrate = askCalibrateReaders()

    maybeSecondaryAxis = askSecondaryAxis()
    if maybeSecondaryAxis:
        secondAxisTitle = maybeSecondaryAxis
    else:
        secondAxisTitle = ""
    return savePath, numReaders, scanRate, calibrate, secondAxisTitle


def guidedSetupFoaming(root, baseSavePath):
    second_win = tk.Toplevel(root)
    second_win.maxsize(1, 1)
    root.eval(f'tk::PlaceWindow {str(second_win)} center')
    second_win.withdraw()
    savePath = setSavePath(second_win, baseSavePath)
    numReaders = askNumReaders(second_win)
    numReaders = int(numReaders)
    scanRate = askScanRate(second_win)
    scanRate = scanRate
    second_win.destroy()
    calibrate = askCalibrateReaders()

    maybeSecondaryAxis = askSecondaryAxis()
    if maybeSecondaryAxis:
        secondAxisTitle = maybeSecondaryAxis
    else:
        secondAxisTitle = ""
    return savePath, numReaders, scanRate, calibrate, secondAxisTitle


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
