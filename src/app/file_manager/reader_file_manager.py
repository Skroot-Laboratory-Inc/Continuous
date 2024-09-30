from src.app.helper.helper_functions import getDesktopLocation


class ReaderFileManager:
    def __init__(self, globalSavePath, readerNumber):
        self.globalSavePath = globalSavePath
        self.readerSavePath = rf'{globalSavePath}/Reader {readerNumber}'
        self.analyzed = rf"{self.readerSavePath}/Analyzed.csv"
        self.smoothAnalyzed = rf"{self.readerSavePath}/smoothAnalyzed.csv"
        self.calibrationLocalLocation = f'{self.readerSavePath}/Calibration.csv'
        self.calibrationGlobalLocation = f'{getDesktopLocation()}/Backend/Calibration/{readerNumber}/Calibration.csv'
        self.summaryPdf = f'{self.globalSavePath}/Summary.pdf'
        self.readerPlotJpg = f'{self.globalSavePath}/Reader {readerNumber}.jpg'
        self.accelerationCsv = f'{self.readerSavePath}/Acceleration.csv'
        self.scanNumber = 100001

    def getReaderSavePath(self):
        return self.readerSavePath

    def getGlobalSavePath(self):
        return self.globalSavePath

    def getAnalyzed(self):
        return self.analyzed

    def getSmoothAnalyzed(self):
        return self.smoothAnalyzed

    def getCalibrationLocalLocation(self):
        return self.calibrationLocalLocation

    def getCalibrationGlobalLocation(self):
        return self.calibrationGlobalLocation

    def getSummaryPdf(self):
        return self.summaryPdf

    def getReaderPlotJpg(self):
        return self.readerPlotJpg

    def getAccelerationCsv(self):
        return self.accelerationCsv

    def getCurrentScanNumber(self):
        return self.scanNumber

    def incrementScanNumber(self, increment):
        self.scanNumber += increment
        return self.scanNumber

    def getCurrentScan(self):
        return f"{self.readerSavePath}/{self.scanNumber}.csv"
