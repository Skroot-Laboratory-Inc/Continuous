from src.app.helper.helper_functions import getDesktopLocation


class ReaderFileManager:
    def __init__(self, globalSavePath, readerNumber):
        self.globalSavePath = globalSavePath
        self.readerSavePath = rf'{globalSavePath}/Reader {readerNumber}'
        self.analyzed = rf"{self.readerSavePath}/Analyzed.csv"
        self.secondAxis = f'{self.readerSavePath}/secondAxis.csv'
        self.smoothAnalyzed = rf"{self.readerSavePath}/smoothAnalyzed.csv"
        self.calibrationLocalLocation = f'{self.readerSavePath}/Calibration.csv'
        self.calibrationGlobalLocation = f'{getDesktopLocation()}/Calibration/{readerNumber}/Calibration.csv'
        self.serverInfo = rf"{self.readerSavePath}/serverInfo.json"
        self.summaryPdf = f'{self.globalSavePath}/Summary.pdf'
        self.readerPlotJpg = f'{self.globalSavePath}/Reader {readerNumber}.jpg'
        self.experimentNotesTxt = f'{self.readerSavePath}/notes.txt'
        self.scanNumber = 100001

    def getReaderSavePath(self):
        return self.readerSavePath

    def getGlobalSavePath(self):
        return self.globalSavePath

    def getAnalyzed(self):
        return self.analyzed

    def getSmoothAnalyzed(self):
        return self.smoothAnalyzed

    def getServerInfo(self):
        return self.serverInfo

    def getCalibrationLocalLocation(self):
        return self.calibrationLocalLocation

    def getCalibrationGlobalLocation(self):
        return self.calibrationGlobalLocation

    def getSecondAxis(self):
        return self.secondAxis

    def getSummaryPdf(self):
        return self.summaryPdf

    def getReaderPlotJpg(self):
        return self.readerPlotJpg

    def getExperimentNotes(self):
        return self.experimentNotesTxt

    def getCurrentScanNumber(self):
        return self.scanNumber

    def incrementScanNumber(self, increment):
        self.scanNumber += increment
        return self.scanNumber

    def getCurrentScan(self):
        return f"{self.readerSavePath}/{self.scanNumber}.csv"
