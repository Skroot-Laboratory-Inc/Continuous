import csv
import datetime
import logging
import os
import platform
import random
import re
import shutil
import string
import subprocess
import time

import numpy as np
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from src.app.authentication.helpers.logging import logAuthAction
from src.app.custom_exceptions.common_exceptions import USBDriveNotFoundException
from src.app.custom_exceptions.sib_exception import NoSibFound
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.data_helpers import convertListToPercent
from src.app.model.sweep_data import SweepData
from src.app.properties.common_properties import CommonProperties
from src.app.properties.hardware_properties import HardwareProperties
from src.app.properties.usb_properties import USBProperties
from src.app.reader.sib.sib_properties import SibProperties
from src.app.widget import text_notification


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


def getCpuTemp():
    """ Get the Raspberry Pi CPU operating temperature """
    if platform.system() == "Windows":
        return np.nan
    try:
        result = subprocess.run(
            ['sudo', 'vcgencmd', 'measure_temp'],
            capture_output=True, text=True, check=True,
        )
        # Parse the output (format: "temp=42.8'C")
        temp_str = result.stdout.strip()
        temp_value = float(temp_str.split('=')[1].split("'")[0])
        return temp_value
    except (subprocess.CalledProcessError, ValueError, IndexError):
        logging.exception("Error reading temperature", extra={"id": "Temperature Reading"})
        return np.nan


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
        return "D:\\"


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


def getStringEnvFlag(varName: str, defaultValue: str) -> str:
    """Read a boolean flag from /etc/environment"""
    result = subprocess.run(
        f"sudo grep '^{varName}=' /etc/environment || echo '{varName}={defaultValue}'",
        shell=True, text=True, capture_output=True
    )

    if result.returncode == 0:
        setting = result.stdout.strip().split('=', 1)[1].strip('"\'')
    else:
        setting = ""
        logging.info(f"Failed to get configuration for {varName}", extra={"id": "configuration"})
    return setting


def setStringEnvFlag(varName: str, newSetting: str):
    """Set a boolean flag in /etc/environment"""
    if platform.system() == "Linux":
        varExists = subprocess.run(f"sudo grep -q '^{varName}=' /etc/environment", shell=True).returncode == 0
        if varExists:
            escaped_value = re.escape(newSetting)
            process = f'sudo sed -i "s#^{varName}=.*#{varName}=\\"{escaped_value}\\"#" /etc/environment'
        else:
            process = f'echo \'{varName}="{newSetting}"\' | sudo tee -a /etc/environment'
        result = subprocess.run(process, shell=True, check=True)
        if result.returncode == 0:
            logging.info(f"Configuration {varName} set to {newSetting}", extra={"id": "configuration"})
        else:
            logging.info(f"Failed to set configuration {varName} to {newSetting}", extra={"id": "configuration"})


def getFloatEnvFlag(varName: str, defaultValue: float) -> float:
    """Read a float value from /etc/environment"""
    value = defaultValue
    result = subprocess.run(
        f"sudo grep '^{varName}=' /etc/environment || echo '{varName}={defaultValue}'",
        shell=True, text=True, capture_output=True
    )

    if result.returncode == 0:
        setting = result.stdout.strip().split('=', 1)[1].strip('"\'')
        try:
            value = float(setting)
        except ValueError:
            logging.warning(f"Invalid float value for {varName}: '{setting}', using default {defaultValue}",
                            extra={"id": "configuration"})
            value = defaultValue
    else:
        logging.info(f"Failed to get configuration for {varName}", extra={"id": "configuration"})

    return value


def setFloatEnvFlag(varName: str, newSetting: float):
    """Set a float value in /etc/environment"""
    if platform.system() == "Linux":
        floatValue = str(newSetting)
        varExists = subprocess.run(f"sudo grep -q '^{varName}=' /etc/environment", shell=True).returncode == 0
        if varExists:
            process = f'sudo sed -i "s/^{varName}=.*/{varName}=\\"{floatValue}\\"/" /etc/environment'
        else:
            process = f'echo \'{varName}="{floatValue}"\' | sudo tee -a /etc/environment'
        result = subprocess.run(process, shell=True, check=True)
        if result.returncode == 0:
            logging.info(f"Configuration {varName} set to {floatValue}", extra={"id": "configuration"})
        else:
            logging.info(f"Failed to set configuration {varName} to {floatValue}", extra={"id": "configuration"})


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


def setDatetimeTimezone(newDatetime, timezone, user: str):
    """
    Set date, time, and timezone on Ubuntu
    Args:
        newDatetime: datetime object or string in format 'YYYY-MM-DD HH:MM:SS'
        timezone: timezone string like 'America/New_York' or 'UTC'
        user: the user that initiated the reset
    """
    currentDatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        if platform.system() != "Linux":
            print("Date/time setting is only supported on Linux systems.")
            return
        logAuthAction(
            "System Time Change",
            "Initiated",
            user,
        )
        currentTimezone = getTimezone()
        subprocess.run(['sudo', 'timedatectl', 'set-timezone', timezone], check=True)
        time.tzset()

        time_str = newDatetime.strftime('%Y-%m-%d %H:%M:%S')
        subprocess.run(['sudo', 'date', '-s', time_str], check=True)
        subprocess.run(['sudo', 'hwclock', '--systohc'], check=True)
        text_notification.setText(f"System time changed to {time_str} ({timezone})")
        logAuthAction(
            "System Time Change",
            f"Changed",
            user,
            result=f"From {currentDatetime} ({currentTimezone}) to {time_str} ({timezone})"
        )
    except subprocess.CalledProcessError as e:
        text_notification.setText(f"System time change failed.")
        logging.exception(f"Error setting date/time: {e}", extra={"id": "Time Setting"})
        logAuthAction(
            "System Time Change",
            f"Failed",
            user,
            result=f"Time unchanged"
        )


def getTimezone():
    try:
        result = subprocess.run(
            ['timedatectl', 'show', '-p', 'Timezone', '--value'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()  # Returns "US/Arizona"
    except:
        return "US/Central"


def getTimezoneOptions():
    return [
        'US/Hawaii',
        'US/Alaska',
        'US/Pacific',
        'US/Mountain',
        'US/Central',
        'US/Eastern',
        'US/Arizona'
    ]


def copyExperimentLog(destinationDirectory: str):
    shutil.copy(f"{CommonFileManager().getExperimentLogDir()}/log.txt", destinationDirectory)


def createScanFile(outputFileName: str, sweepData: SweepData):
    volts = convertListToPercent(sweepData.getMagnitude())
    with open(outputFileName, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency (MHz)', SibProperties.getContinuousProperties().yAxisLabel])
        writer.writerows(zip(sweepData.getFrequency(), volts))


if __name__ == "__main__":
    print(getTimezone())
    print(getTimezoneOptions())
