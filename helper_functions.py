import os
import tkinter as tk
import zipfile

import startfile

import text_notification


def frequencyToIndex(zeroPoint, frequencyVector):
    return [100*(1 - val/zeroPoint) for val in frequencyVector]


def openFileExplorer(path):
    startfile.startfile(path)


def downloadAsZip(path, zipName):
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
    truncatedX, truncatedY = [], []
    for index, xval in enumerate(x):
        if minX < xval < maxX:
            truncatedX.append(xval)
            truncatedY.append(y[index])
    return truncatedX, truncatedY

