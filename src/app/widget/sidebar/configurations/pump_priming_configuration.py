from src.app.helper_methods.configuration_constants import ConfigurationConstants
from src.app.helper_methods.helper_functions import getFloatEnvFlag, setFloatEnvFlag
from src.app.properties.dev_properties import DevProperties
from src.app.properties.pump_properties import PumpProperties


class PumpPrimingConfiguration:
    def __init__(self):
        if not DevProperties().isDevMode:
            self.defaultPrimingFlowRate = getFloatEnvFlag(
                ConfigurationConstants().defaultPrimingFlowRate,
                PumpProperties().defaultPrimingFlowRate,
            )
        else:
            self.defaultPrimingFlowRate = PumpProperties().defaultPrimingFlowRate

    def setConfig(self, newSetting: float):
        self.defaultPrimingFlowRate = newSetting
        setFloatEnvFlag(ConfigurationConstants().defaultPrimingFlowRate, newSetting)

    def getConfig(self) -> float:
        return self.defaultPrimingFlowRate
