from src.app.helper_methods.configuration_constants import ConfigurationConstants
from src.app.helper_methods.helper_functions import getStringEnvFlag, setStringEnvFlag
from src.app.properties.dev_properties import DevProperties
from src.app.properties.secondary_axis_properties import SecondaryAxisProperties


class SecondaryAxisUnits:
    def __init__(self):
        if not DevProperties().isDevMode:
            self.secondaryAxisUnits = getStringEnvFlag(
                ConfigurationConstants().secondaryAxisUnit,
                SecondaryAxisProperties().defaultUnit,
            )
        else:
            self.secondaryAxisUnits = SecondaryAxisProperties().defaultUnit

    def setConfig(self, newSetting: str):
        self.secondaryAxisUnits = newSetting
        setStringEnvFlag(ConfigurationConstants().secondaryAxisUnit, newSetting)

    def getConfig(self):
        return self.secondaryAxisUnits
