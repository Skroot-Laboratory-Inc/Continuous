import glob
import os
import shutil

import pandas

from src.app.model.sweep_data import SweepData
from src.app.properties.dev_properties import DevProperties
from src.app.properties.sib_properties import SibProperties
from src.app.reader.sib.sib_interface import SibInterface


class DevSib(SibInterface):
    def __init__(self, readerNumber):
        Properties = SibProperties()
        self.DevProperties = DevProperties()
        self.yAxisLabel = Properties.yAxisLabel
        self.devFiles = glob.glob(f'{self.DevProperties.devBaseFolder}/{readerNumber}/1*.csv')
        self.currentDevFileIndex, self.currentDevFile = next(
            (x, val) for x, val in enumerate(self.devFiles)
            if float(os.path.basename(val)[0:-4]) > self.DevProperties.startTime + 100000
        )

    def takeScan(self, outputFilename, disableSaveFiles) -> SweepData:
        self.currentDevFileIndex += 1
        currentScanFile = self.devFiles[self.currentDevFileIndex]
        readings = pandas.read_csv(currentScanFile)
        if not disableSaveFiles:
            shutil.copy(currentScanFile, outputFilename)
        return SweepData(
            readings['Frequency (MHz)'].values.tolist(),
            readings[self.yAxisLabel].values.tolist(),
        )

    def getYAxisLabel(self) -> str:
        return self.yAxisLabel

    def loadCalibrationFile(self):
        return True

    def calibrateIfRequired(self):
        self.takeCalibrationScan()

    def takeCalibrationScan(self) -> bool:
        return True

    def setStartFrequency(self, startFreqMHz) -> bool:
        return True

    def setStopFrequency(self, stopFreqMHz) -> bool:
        return True

