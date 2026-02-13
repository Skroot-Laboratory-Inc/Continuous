import csv
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from scipy.optimize import curve_fit


EXPECTED_COLUMNS = ['Frequency (MHz)', 'Signal Strength (Unitless)']


def gaussian(x, amplitude, centroid, std):
    return amplitude * np.exp(-(x - centroid) ** 2 / (2 * std ** 2))


def loadScanFile():
    root = tk.Tk()
    root.withdraw()
    filePath = filedialog.askopenfilename(
        title="Select a scan file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    )
    root.destroy()
    if not filePath:
        return None

    with open(filePath, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)

    header = [col.strip() for col in header]
    if header != EXPECTED_COLUMNS:
        messagebox.showerror(
            "Improper Format",
            f"The selected file has incorrect columns.\n\n"
            f"Expected:\n  {', '.join(EXPECTED_COLUMNS)}\n\n"
            f"Found:\n  {', '.join(header)}"
        )
        return None

    frequency = []
    magnitude = []
    with open(filePath, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            frequency.append(float(row[EXPECTED_COLUMNS[0]]))
            magnitude.append(float(row[EXPECTED_COLUMNS[1]]))

    return np.array(frequency), np.array(magnitude)


def analyzeScanFile(frequency, magnitude, windowMHz=5):
    rangeMask = (frequency >= 110) & (frequency <= 160)
    frequency = frequency[rangeMask]
    magnitude = magnitude[rangeMask]

    maxIdx = np.argmax(magnitude)
    peakFreq = frequency[maxIdx]

    mask = (frequency >= peakFreq - windowMHz) & (frequency <= peakFreq + windowMHz)
    xAroundPeak = frequency[mask]
    yAroundPeak = magnitude[mask]

    popt, _ = curve_fit(
        gaussian,
        xAroundPeak,
        yAroundPeak,
        p0=(max(magnitude), frequency[maxIdx], 1),
        bounds=([min(magnitude), min(xAroundPeak), 0], [max(magnitude), max(xAroundPeak), np.inf]),
    )

    amplitude, centroid, std = popt

    yPredicted = gaussian(xAroundPeak, *popt)
    ssRes = np.sum((yAroundPeak - yPredicted) ** 2)
    ssTot = np.sum((yAroundPeak - np.mean(yAroundPeak)) ** 2)
    rSquared = 1 - (ssRes / ssTot) if ssTot != 0 else 0.0

    maxFrequency = frequency[maxIdx]
    equation = f"y = {amplitude:.4f} * exp(-(x - {centroid:.4f})^2 / (2 * {std:.4f}^2))"

    return maxFrequency, equation, rSquared


if __name__ == "__main__":
    data = loadScanFile()
    if data is not None:
        frequency, magnitude = data
        maxFrequency, equation, rSquared = analyzeScanFile(frequency, magnitude)
        print(f"Max Frequency (no smoothing): {maxFrequency} MHz")
        print(f"Gaussian Fit Equation: {equation}")
        print(f"R² Value: {rSquared:.6f}")
