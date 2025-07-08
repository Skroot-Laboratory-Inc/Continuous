import csv
import logging
import os
import platform
import random
import string
import subprocess

import numpy as np
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from src.app.authentication.helpers.functions import setFileOwner
from src.app.custom_exceptions.common_exceptions import USBDriveNotFoundException
from src.app.custom_exceptions.sib_exception import NoSibFound
from src.app.helper_methods.data_helpers import convertListToPercent
from src.app.model.sweep_data import SweepData
from src.app.properties.common_properties import CommonProperties
from src.app.properties.hardware_properties import HardwareProperties
from src.app.properties.sib_properties import SibProperties
from src.app.properties.usb_properties import USBProperties


def getSibPort() -> ListPortInfo:
    ports = list_ports.comports()
    if platform.system() == "Windows":
        filteredPorts = [port for port in ports if "USB Serial Device" in port.description]
    else:
        filteredPorts = [port for port in ports if port.manufacturer == HardwareProperties().skrootManufacturer]
    if filteredPorts:
        return filteredPorts[0]
    raise NoSibFound()


def restartPc():
    if platform.system() == "Linux":
        subprocess.Popen(['sudo', "reboot"], stdin=subprocess.PIPE)


def getUsbDrive():
    """Find USB drives attached and mounts them to a temporary drive location. """
    if platform.system() == "Linux":
        for symLink in USBProperties().symLinkPaths:
            if os.path.exists(symLink):
                subprocess.run(["sudo", "mount", "-o", "umask=000", symLink, USBProperties().driveDir])
                if os.path.ismount(USBProperties().driveDir) and os.access(USBProperties().driveDir, os.W_OK):
                    return USBProperties().driveDir
                else:
                    unmountUSBDrive()
        raise USBDriveNotFoundException()
    else:
        return "H:\\"


def unmountUSBDrive():
    """ Unmounts the USB drive from the temporary mount location. """
    subprocess.Popen(["sudo", "umount", USBProperties().driveDir])


def getBoolEnvFlag(varName: str, defaultValue: bool) -> bool:
    """Read a boolean flag from /etc/environment"""
    enabled = True
    result = subprocess.run(
        f"sudo grep '^{varName}=' /etc/environment || echo '{varName}={defaultValue}'",
        shell=True, text=True, capture_output=True
    )

    if result.returncode == 0:
        setting = result.stdout.strip().split('=', 1)[1].lower().strip('"\'')
        enabled = setting == 'true'
    else:
        logging.info(f"Failed to get configuration for {varName}", extra={"id": "configuration"})
    return enabled


def setBoolEnvFlag(varName: str, newSetting: bool):
    """Set a boolean flag in /etc/environment"""
    if platform.system() == "Linux":
        boolValue = 'true' if newSetting else 'false'
        varExists = subprocess.run(f"sudo grep -q '^{varName}=' /etc/environment", shell=True).returncode == 0
        if varExists:
            process = f'sudo sed -i "s/^{varName}=.*/{varName}=\\"{boolValue}\\"/" /etc/environment'
        else:
            process = f'echo \'{varName}="{boolValue}"\' | sudo tee -a /etc/environment'
        result = subprocess.run(process, shell=True, check=True)
        if result.returncode == 0:
            logging.info(f"Configuration {varName} set to {boolValue}", extra={"id": "configuration"})
        else:
            logging.info(f"Failed to set configuration {varName} to {boolValue}", extra={"id": "configuration"})


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


def generateLotId() -> str:
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=CommonProperties().lotIdLength))

