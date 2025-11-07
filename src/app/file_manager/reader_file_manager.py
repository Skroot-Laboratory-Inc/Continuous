import os
from datetime import datetime

from src.app.helper_methods.datetime_helpers import datetimeToMillis


class ReaderFileManager:
    def __init__(self, globalSavePath, readerNumber):
        self.readerSavePath = globalSavePath
        self.analyzed = rf"{self.readerSavePath}/Analyzed.csv"
        self.temperatureCsv = rf'{self.readerSavePath}/temperature.csv'
        self.smoothAnalyzed = rf"{self.readerSavePath}/smoothAnalyzed.csv"
        self.secondAxis = rf"{self.readerSavePath}/secondAxis.csv"
        self.calibrationLocalLocation = f'{self.readerSavePath}/Calibration.csv'
        self.calibrationGlobalLocation = f'{getDesktopLocation()}/Backend/Calibration/{readerNumber}/Calibration.csv'
        self.readerPlotJpg = f'{self.readerSavePath}/Result Figure.jpg'
        self.accelerationCsv = f'{self.readerSavePath}/Acceleration.csv'
        self.scanDateMillis = datetimeToMillis(datetime.now())

    def getReaderSavePath(self) -> str:
        return self.readerSavePath

    def getTemperatureCsv(self) -> str:
        return self.temperatureCsv

    def getAnalyzed(self) -> str:
        return self.analyzed

    def getSmoothAnalyzed(self) -> str:
        return self.smoothAnalyzed

    def getSecondAxis(self) -> str:
        return self.secondAxis

    def getCalibrationLocalLocation(self) -> str:
        return self.calibrationLocalLocation

    def getCalibrationGlobalLocation(self) -> str:
        return self.calibrationGlobalLocation

    def getReaderPlotJpg(self) -> str:
        return self.readerPlotJpg

    def getCurrentScanDate(self) -> int:
        return self.scanDateMillis

    def updateScanName(self):
        self.scanDateMillis = datetimeToMillis(datetime.now())

    def getCurrentScan(self) -> str:
        return f"{self.readerSavePath}/{self.scanDateMillis}.csv"


def getDesktopLocation() -> str:
    """ This gets the path to the computer's desktop. """
    try:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except KeyError:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
