import datetime
import os
import platform
import random
import stat
import string
import subprocess
import tkinter as tk
import zipfile
from tkinter import messagebox

import numpy as np
import startfile

from src.app.helper.vertical_scrolled_frame import VerticalScrolledFrame
from src.app.properties.common_properties import CommonProperties
from src.app.widget import text_notification


def frequencyToIndex(zeroPoint, frequencyVector):
    """ This converts a frequency vector into SGI """
    return [100 * (1 - val / zeroPoint) for val in frequencyVector]


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


def millisToDatetime(millis: int):
    """ This converts from milliseconds to a datetime object. """
    return datetime.datetime.fromtimestamp(millis / 1000)


def gaussian(x, amplitude, centroid, std):
    """ Standard gaussian fit. """
    return amplitude * np.exp(-(x - centroid) ** 2 / (2 * std ** 2))


def datetimeToMillis(dt: datetime.datetime):
    """ This converts from a datetime object to epoch millis. """
    return int(dt.timestamp() * 1000)


def datetimeToDisplay(dt: datetime.datetime):
    """ Converts a datetime to a string. i.e. Mon Jan 3rd 5:50 PM """
    if dt is not None:
        return dt.strftime('%a %b %d %I:%M %p')
    else:
        return None


def convertToPercent(item):
    """ This converts a single value into a percent i.e. 1.08 into 8%"""
    return (item - 1) * 100


def isMenuOptionPresent(menu_bar, menu_label):
    """
    Function to check if a menu is already present in the menubar.

    Parameters:
    - menu_bar (tk.Menu): The menubar to check.
    - menu_label (str): The label of the menu to check for.

    Returns:
    - bool: True if the menu is present, False otherwise.
    """
    for index in range(menu_bar.index("end") + 1):
        if menu_bar.type(index) == "cascade" and menu_bar.entrycget(index, "label") == menu_label:
            return True
    return False


def getDesktopLocation():
    """ This gets the path to the computer's desktop. """
    try:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except KeyError:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')


def getSibPowerStatus(hubReaderPath):
    return subprocess.run(['cat', f'/sys/bus/usb/devices/{hubReaderPath}/power/runtime_status']).stdout


def getCwd():
    """ This gets the directory the app is being run from i.e. the path to main.py. """
    return os.getcwd()


def runShScript(shScriptFilename, experimentLog):
    """ This runs an sh script as the sudo user, and overwrites the log file with the results. """
    st = os.stat(shScriptFilename)
    os.chmod(shScriptFilename, st.st_mode | stat.S_IEXEC)
    logFile = open(experimentLog, 'w+')
    process = subprocess.Popen(["sudo", "-SH", "sh", shScriptFilename], stdout=logFile, stderr=logFile,
                               stdin=subprocess.PIPE, cwd=os.path.dirname(shScriptFilename))
    process.communicate("skroot".encode())
    process.wait()


def formatDate(date):
    return date.isoformat()


def centerWindowOnFrame(window, frame):
    window.update()
    frame_x = frame.winfo_x()
    frame_y = frame.winfo_y()
    center_x = frame_x + (frame.winfo_width() // 2)
    center_y = frame_y + (frame.winfo_height() // 2)
    x = center_x - (window.winfo_width() // 2)
    y = center_y - (window.winfo_height() // 2)
    window.geometry('+%d+%d' % (x, y))


def formatDatetime(date: datetime.datetime):
    return date.strftime('%m/%d/%Y %I:%M:%S %p')


def getZeroPoint(equilibrationTime, frequencies):
    lastFrequencyPoint = frequencies[-1]
    zeroPoint = np.nan
    pointsUsed = 5
    if equilibrationTime == 0 and lastFrequencyPoint != np.nan and lastFrequencyPoint != 0:
        return frequencies[-1]
    elif equilibrationTime == 0 and (lastFrequencyPoint == np.nan or lastFrequencyPoint == 0):
        raise Exception()
    else:
        while np.isnan(zeroPoint):
            zeroPoint = np.nanmean(frequencies[-pointsUsed:])
            pointsUsed += 5
            if pointsUsed > 100:
                zeroPoint = np.nanmean(frequencies)
                break
        return zeroPoint


def makeToplevelScrollable(windowRoot, fillOutWindowFn):
    windowRoot.minsize(width=650, height=550)
    windowRoot.maxsize(width=800, height=550)
    window = VerticalScrolledFrame(windowRoot, bg='white', borderwidth=0, height=800, width=600)
    fillOutWindowFn(window.interior)
    window.pack(expand=True, fill=tk.BOTH)
    return windowRoot, window.interior


def confirmAndPowerDown():
    endExperiment = messagebox.askquestion(
        f'Shut down PC',
        f'Are you sure you wish to shutdown the PC?')
    if endExperiment == 'yes':
        shutdown()


def shutdown():
    if platform.system() == "Linux":
        process = subprocess.Popen(['sudo', "-S", 'shutdown', 'now'], stdin=subprocess.PIPE)
        process.communicate("skroot".encode())


def restart():
    if platform.system() == "Linux":
        subprocess.Popen(["systemctl", 'reboot', '-i'], stdin=subprocess.PIPE)


def shouldRestart():
    response = messagebox.askquestion(
        f'Restart Required',
        f'Software update will require the system to restart. Are you sure you would like to continue?')
    if response == "yes":
        return True
    else:
        return False


def destroyKeyboard():
    subprocess.Popen(["pkill", "onboard"])


def generateLotId() -> str:
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=CommonProperties().lotIdLength))
