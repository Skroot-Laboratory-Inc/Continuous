from datetime import datetime

from src.app.helper_methods.datetime_helpers import datetimeToMillis, formatDate
from src.app.helper_methods.helper_functions import generateLotId
from src.app.use_case.configuration.setup_form_config import SetupFormConfig
from src.app.widget.sidebar.configurations.pump_configuration import PumpConfiguration


class SetupReaderFormInput:
    def __init__(self, config: SetupFormConfig):
        """
        Initialize SetupReaderFormInput with use-case-specific configuration.

        Args:
            config: SetupFormConfig for use-case-specific defaults and options.
        """
        self.date = datetime.now()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year
        self.scanRate = config.defaultScanRate
        self.calibrate = config.defaultCalibrate
        self.pumpFlowRate = PumpConfiguration().getConfig()
        self.lotId = generateLotId()
        self.equilibrationTime = config.defaultEquilibrationTime
        self.savePath = ""

    def getMonth(self) -> int:
        return self.month

    def getPumpFlowRate(self) -> float:
        return self.pumpFlowRate

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

    def getWarehouse(self) -> str:
        return self.warehouse

    def resetRun(self):
        self.date = datetime.now()
        self.pumpFlowRate = PumpConfiguration().getConfig()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year
        self.lotId = generateLotId()
        return self

