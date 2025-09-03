import socket
from datetime import datetime

from src.app.helper_methods.datetime_helpers import datetimeToMillis, formatDate
from src.app.helper_methods.helper_functions import generateLotId
from src.app.properties.pump_properties import PumpProperties
from src.app.properties.setup_reader_form_defaults import SetupReaderFormDefaults


class SetupReaderFormInput:
    def __init__(self):
        setupReaderFormDefaults = SetupReaderFormDefaults()
        self.date = datetime.now()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year
        self.scanRate = setupReaderFormDefaults.scanRate
        self.calibrate = setupReaderFormDefaults.calibrate
        self.pumpRpm = PumpProperties().defaultRpm
        self.lotId = generateLotId()
        self.equilibrationTime = setupReaderFormDefaults.equilibrationTime
        self.savePath = ""

    def getMonth(self) -> int:
        return self.month

    def getPumpRpm(self) -> float:
        return self.pumpRpm

    def getDay(self) -> int:
        return self.day

    def getYear(self) -> int:
        return self.year

    def getDate(self):
        self.date = datetime.now()
        return formatDate(self.date.date())

    def getDateMillis(self) -> int:
        return datetimeToMillis(self.date)

    def getScanRate(self) -> float:
        return float(self.scanRate)

    def getCalibrate(self) -> bool:
        return self.calibrate

    def getLotId(self) -> str:
        return self.lotId

    def getEquilibrationTime(self) -> float:
        return float(self.equilibrationTime)

    def getSavePath(self) -> str:
        return self.savePath

    def resetRun(self):
        self.date = datetime.now()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year
        self.lotId = generateLotId()
        return self

