import tkinter as tk


def askDate(root):
    date = ''
    while date == '':
        date = tk.simpledialog.askinteger(f"Today's Date", "Enter today's date (YYYYMMDD)", parent=root,
                                          minvalue=20230630)
    return date


def askVesselType():
    vessel = None
    while vessel is None:
        vessel = tk.simpledialog.askstring(f"Vessel Type", "Enter the vessel you are using")
    return vessel


def askCellType():
    cell = None
    while cell is None:
        cell = tk.simpledialog.askstring(f"Cell Type", "Enter the cells you are growing.")
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
