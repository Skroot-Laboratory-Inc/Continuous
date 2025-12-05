from datetime import datetime
from typing import Optional

from src.app.helper_methods.datetime_helpers import datetimeToMillis, formatDate
from src.app.helper_methods.helper_functions import generateLotId
from src.app.properties.setup_reader_form_defaults import SetupReaderFormDefaults
from src.app.widget.sidebar.configurations.pump_configuration import PumpConfiguration


class SetupReaderFormInput:
    def __init__(self, config: Optional['SetupFormConfig'] = None):
        """
        Initialize SetupReaderFormInput with optional use-case-specific configuration.

        Args:
            config: Optional SetupFormConfig for use-case-specific defaults.
                   If None, uses the legacy SetupReaderFormDefaults.
        """
        # Use config defaults if provided, otherwise fall back to legacy defaults
        if config is not None:
            scan_rate = config.default_scan_rate
            calibrate = config.default_calibrate
            equilibration_time = config.default_equilibration_time
        else:
            setupReaderFormDefaults = SetupReaderFormDefaults()
            scan_rate = setupReaderFormDefaults.scanRate
            calibrate = setupReaderFormDefaults.calibrate
            equilibration_time = setupReaderFormDefaults.equilibrationTime

        self.date = datetime.now()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year
        self.scanRate = scan_rate
        self.calibrate = calibrate
        self.pumpFlowRate = PumpConfiguration().getConfig()
        self.lotId = generateLotId()
        self.equilibrationTime = equilibration_time
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

    def resetRun(self):
        self.date = datetime.now()
        self.pumpFlowRate = PumpConfiguration().getConfig()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year
        self.lotId = generateLotId()
        return self

    def resetFlowRate(self):
        self.pumpFlowRate = PumpConfiguration().getConfig()
        return self

