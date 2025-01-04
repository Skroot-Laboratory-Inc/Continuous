import random
import socket
import string
from datetime import datetime

from src.app.helper.helper_functions import formatDate, datetimeToMillis, generateLotId
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
        self.lotId = generateLotId()
        self.incubator = socket.gethostname()
        self.equilibrationTime = setupReaderFormDefaults.equilibrationTime
        self.savePath = ""

    def getMonth(self) -> int:
        return self.month

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

    def getIncubator(self) -> str:
        return self.incubator

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

