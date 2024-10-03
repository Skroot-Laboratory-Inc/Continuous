from datetime import datetime

from src.app.helper.helper_functions import formatDate, datetimeToMillis
from src.app.properties.guided_setup_defaults import GuidedSetupDefaults


class GuidedSetupInput:
    def __init__(self):
        guidedSetupDefaults = GuidedSetupDefaults()
        self.date = datetime.now()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year
        self.scanRate = guidedSetupDefaults.scanRate
        self.calibrate = guidedSetupDefaults.calibrate
        self.experimentId = guidedSetupDefaults.experimentId
        self.equilibrationTime = guidedSetupDefaults.equilibrationTime
        self.savePath = ""

    def getMonth(self) -> int:
        return self.month

    def getDay(self) -> int:
        return self.day

    def getYear(self) -> int:
        return self.year

    def getDate(self):
        return formatDate(self.date.date())

    def getDateMillis(self) -> int:
        return datetimeToMillis(self.date)

    def getScanRate(self) -> float:
        return float(self.scanRate)

    def getCalibrate(self) -> bool:
        return self.calibrate

    def getExperimentId(self) -> str:
        return self.experimentId

    def getEquilibrationTime(self) -> float:
        return float(self.equilibrationTime)

    def getSavePath(self) -> str:
        return self.savePath

