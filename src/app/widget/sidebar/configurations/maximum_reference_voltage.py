from src.app.helper_methods.helper_functions import getFloatEnvFlag, setFloatEnvFlag
from src.app.properties.dev_properties import DevProperties
from src.app.widget.sidebar.configurations.constants import ScanPropertyConstants


class MaximumReferenceVoltageConfiguration:
    def __init__(self):
        if not DevProperties().isDevMode:
            self.maximumReferenceVoltage = getFloatEnvFlag(
                ScanPropertyConstants().maximumReferenceVoltageConfig,
                ScanPropertyConstants().defaultMaximumReferenceVoltage,
            )
        else:
            self.maximumReferenceVoltage = ScanPropertyConstants().defaultMaximumReferenceVoltage

    def setConfig(self, newSetting: float):
        self.maximumReferenceVoltage = newSetting
        setFloatEnvFlag(ScanPropertyConstants().maximumReferenceVoltageConfig, newSetting)

    def getConfig(self):
        return self.maximumReferenceVoltage
