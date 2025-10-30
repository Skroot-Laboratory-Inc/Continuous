from src.app.helper_methods.configuration_constants import ConfigurationConstants
from src.app.helper_methods.helper_functions import getStringEnvFlag, setStringEnvFlag
from src.app.properties.dev_properties import DevProperties
from src.app.properties.secondary_axis_properties import SecondaryAxisProperties


class SecondaryAxisType:
    def __init__(self):
        if not DevProperties().isDevMode:
            self.secondaryAxisType = getStringEnvFlag(
                ConfigurationConstants().secondaryAxisType,
                SecondaryAxisProperties().defaultAxisType,
            )
        else:
            self.secondaryAxisType = SecondaryAxisProperties().defaultAxisType

    def setConfig(self, newSetting: str):
        self.secondaryAxisType = newSetting
        setStringEnvFlag(ConfigurationConstants().secondaryAxisType, newSetting)

    def getConfig(self):
        return self.secondaryAxisType
