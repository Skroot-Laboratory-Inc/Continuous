import os


class ReaderFileManager:
    def __init__(self, globalSavePath, readerNumber):
        self.readerSavePath = globalSavePath
        self.analyzed = rf"{self.readerSavePath}/Analyzed.csv"
        self.temperatureCsv = rf'{self.readerSavePath}/temperature.csv'
        self.smoothAnalyzed = rf"{self.readerSavePath}/smoothAnalyzed.csv"
        self.calibrationLocalLocation = f'{self.readerSavePath}/Calibration.csv'
        self.calibrationGlobalLocation = f'{getDesktopLocation()}/Backend/Calibration/{readerNumber}/Calibration.csv'
        self.readerPlotJpg = f'{self.readerSavePath}/Result Figure.jpg'
        self.accelerationCsv = f'{self.readerSavePath}/Acceleration.csv'
        self.scanNumber = 100001

    def getReaderSavePath(self):
        return self.readerSavePath

    def getTemperatureCsv(self):
        return self.temperatureCsv

    def getAnalyzed(self):
        return self.analyzed

    def getSmoothAnalyzed(self):
        return self.smoothAnalyzed

    def getCalibrationLocalLocation(self):
        return self.calibrationLocalLocation

    def getCalibrationGlobalLocation(self):
        return self.calibrationGlobalLocation

    def getReaderPlotJpg(self):
        return self.readerPlotJpg

    def getCurrentScanNumber(self):
        return self.scanNumber

    def incrementScanNumber(self, increment):
        self.scanNumber += increment
        return self.scanNumber

    def getCurrentScan(self):
        return f"{self.readerSavePath}/{self.scanNumber}.csv"


def getDesktopLocation():
    """ This gets the path to the computer's desktop. """
    try:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except KeyError:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
