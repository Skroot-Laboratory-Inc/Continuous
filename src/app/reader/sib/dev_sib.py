import glob
import os
import time

import pandas
from reactivex import Subject
from reactivex.subject import BehaviorSubject

from src.app.helper_methods.model.sweep_data import SweepData
from src.app.use_case.use_case_factory import ContextFactory
from src.app.helper_methods.data_helpers import convertListFromPercent
from src.app.properties.dev_properties import DevProperties
from src.app.reader.sib.sib_interface import SibInterface


class DevSib(SibInterface):
    def __init__(self, readerNumber):
        Properties = ContextFactory().getSibProperties()
        self.DevProperties = DevProperties()
        self.yAxisLabel = Properties.yAxisLabel
        self.devFiles = glob.glob(f'{self.DevProperties.devBaseFolder}/Reader {readerNumber}/1*.csv')
        self.calibrationFilePresent = BehaviorSubject(True)
        self.currentDevFileIndex, self.currentDevFile = next(
            (x, val) for x, val in enumerate(self.devFiles)
            if float(os.path.basename(val)[0:-4]) > self.DevProperties.startTime + 100000
        )
        self.currentlyScanning = Subject()

    def getCurrentlyScanning(self) -> Subject:
        return self.currentlyScanning

    def getCalibrationFilePresent(self) -> BehaviorSubject:
        return self.calibrationFilePresent

    def takeScan(self, directory: str, currentVolts: float, shutdown_flag=None) -> SweepData:
        self.currentDevFileIndex += 1
        currentScanFile = self.devFiles[self.currentDevFileIndex]
        readings = pandas.read_csv(currentScanFile)
        return SweepData(
            readings['Frequency (MHz)'].values.tolist(),
            convertListFromPercent(readings[self.yAxisLabel].values.tolist()),
        )

    def setReferenceFrequency(self, peakFrequencyMHz: float):
        return

    def estimateDuration(self) -> float:
        return DevProperties().devScanTime

    def performHandshake(self) -> bool:
        return True

    def performCalibration(self):
        return self.takeCalibrationScan()

    def loadCalibrationFile(self):
        return True

    def takeCalibrationScan(self) -> bool:
        self.currentlyScanning.on_next(True)
        time.sleep(DevProperties().devScanTime)
        self.currentlyScanning.on_next(False)
        return True

    def setStartFrequency(self, startFreqMHz) -> bool:
        return True

    def setStopFrequency(self, stopFreqMHz) -> bool:
        return True

    def getYAxisLabel(self) -> str:
        return self.yAxisLabel

    def close(self) -> bool:
        return True
