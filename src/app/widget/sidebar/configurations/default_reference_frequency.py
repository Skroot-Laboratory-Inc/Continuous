from src.app.helper_methods.helper_functions import getFloatEnvFlag, setFloatEnvFlag
from src.app.properties.dev_properties import DevProperties
from src.app.widget.sidebar.configurations.constants import ScanPropertyConstants


class ReferenceFrequencyConfiguration:
    def __init__(self):
        if not DevProperties().isDevMode:
            self.referenceFrequency = getFloatEnvFlag(
                ScanPropertyConstants().referenceFrequencyConfig,
                ScanPropertyConstants().defaultReferenceFrequency,
            )
        else:
            self.referenceFrequency = ScanPropertyConstants().defaultReferenceFrequency

    def setConfig(self, newSetting: float):
        self.referenceFrequency = newSetting
        setFloatEnvFlag(ScanPropertyConstants().referenceFrequencyConfig, newSetting)

    def getConfig(self):
        return self.referenceFrequency
