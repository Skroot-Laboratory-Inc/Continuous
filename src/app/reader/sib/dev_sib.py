import glob
import os
import shutil
import time

import pandas
from reactivex import Subject
from reactivex.subject import BehaviorSubject

from src.app.helper_methods.data_helpers import convertListFromPercent
from src.app.model.sweep_data import SweepData
from src.app.properties.dev_properties import DevProperties
from src.app.properties.sib_properties import SibProperties
from src.app.reader.sib.sib_interface import SibInterface


class DevSib(SibInterface):
    def __init__(self, readerNumber):
        Properties = SibProperties()
        self.DevProperties = DevProperties()
        self.yAxisLabel = Properties.yAxisLabel
        self.devFiles = glob.glob(f'{self.DevProperties.devBaseFolder}/Reader {readerNumber}/1*.csv')
        self.calibrationFilePresent = BehaviorSubject(True)
        self.currentDevFileIndex, self.currentDevFile = next(
            (x, val) for x, val in enumerate(self.devFiles)
            if float(os.path.basename(val)[0:-4]) > self.DevProperties.startTime + 100000
        )
        self.currentlyScanning = Subject()

    def getCalibrationFilePresent(self) -> BehaviorSubject:
        return self.calibrationFilePresent

    def takeScan(self, outputFilename, disableSaveFiles) -> SweepData:
        self.currentDevFileIndex += 1
        currentScanFile = self.devFiles[self.currentDevFileIndex]
        readings = pandas.read_csv(currentScanFile)
        if not disableSaveFiles:
            shutil.copy(currentScanFile, outputFilename)
        return SweepData(
            readings['Frequency (MHz)'].values.tolist(),
            convertListFromPercent(readings[self.yAxisLabel].values.tolist()),
        )

    def getYAxisLabel(self) -> str:
        return self.yAxisLabel

    def estimateDuration(self) -> float:
        return DevProperties().devScanTime

    def loadCalibrationFile(self):
        return True

    def performCalibration(self):
        return self.takeCalibrationScan()

    def takeCalibrationScan(self) -> bool:
        self.currentlyScanning.on_next(True)
        time.sleep(DevProperties().devScanTime)
        self.currentlyScanning.on_next(False)
        return True

    def setStartFrequency(self, startFreqMHz) -> bool:
        return True

    def setStopFrequency(self, stopFreqMHz) -> bool:
        return True

    def getCurrentlyScanning(self) -> Subject:
        return self.currentlyScanning
