import os
import tkinter as tk
import zipfile

import startfile

from src.app.widget import text_notification


def frequencyToIndex(zeroPoint, frequencyVector):
    """ This converts a frequency vector into SGI """
    return [100*(1 - val/zeroPoint) for val in frequencyVector]


def openFileExplorer(path):
    """ This function opens the file explorer at the path passed in."""
    startfile.startfile(path)


def downloadAsZip(path, zipName):
    """ This function downloads a directory to a zip file and places it in the directory of the users choosing"""
    saveDirectory = tk.filedialog.askdirectory()
    if saveDirectory != "":
        saveFilename = f"{saveDirectory}/{zipName}"
        text_notification.setText(f"Downloading experiment as zip file to {saveFilename}...")
        with zipfile.ZipFile(saveFilename, 'w') as zipf:
            for foldername, subfolders_, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, path)
                    zipf.write(file_path, arcname)
        text_notification.setText(f"Finished downloading experiment at {saveFilename}")
    else:
        text_notification.setText("No directory selected, download canceled.")

def truncateByX(minX, maxX, x, y):
    """ This truncates all values from two vectors based on a min and max value for x. """
    truncatedX, truncatedY = [], []
    for index, xval in enumerate(x):
        if minX < xval < maxX:
            truncatedX.append(xval)
            truncatedY.append(y[index])
    return truncatedX, truncatedY


def convertListToPercent(list):
    """ This function converts a vector of values to percentages, i.e. 1.08 converts to 8% """
    return [convertToPercent(item) for item in list]


def convertToPercent(item):
    """ This converts a single value into a percent i.e. 1.08 into 8%"""
    return (item-1)*100

