from src.app.helper_methods.helper_functions import getFloatEnvFlag, setFloatEnvFlag
from src.app.properties.dev_properties import DevProperties
from src.app.widget.sidebar.configurations.constants import ScanPropertyConstants


class MinimumReferenceVoltageConfiguration:
    def __init__(self):
        if not DevProperties().isDevMode:
            self.minimumReferenceVoltage = getFloatEnvFlag(
                ScanPropertyConstants().minimumReferenceVoltageConfig,
                ScanPropertyConstants().defaultMinimumReferenceVoltage,
            )
        else:
            self.minimumReferenceVoltage = ScanPropertyConstants().defaultMinimumReferenceVoltage

    def setConfig(self, newSetting: float):
        self.minimumReferenceVoltage = newSetting
        setFloatEnvFlag(ScanPropertyConstants().minimumReferenceVoltageConfig, newSetting)

    def getConfig(self):
        return self.minimumReferenceVoltage
