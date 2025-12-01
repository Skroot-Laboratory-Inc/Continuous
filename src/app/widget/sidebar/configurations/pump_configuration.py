from src.app.helper_methods.configuration_constants import ConfigurationConstants
from src.app.helper_methods.helper_functions import getFloatEnvFlag, setFloatEnvFlag
from src.app.properties.dev_properties import DevProperties
from src.app.properties.pump_properties import PumpProperties


class PumpConfiguration:
    def __init__(self):
        # if not DevProperties().isDevMode:
        #     self.defaultPumpFlowRate = getFloatEnvFlag(
        #         ConfigurationConstants().defaultFlowRate,
        #         PumpProperties().defaultFlowRate,
        #     )
        # else:
        self.defaultPumpFlowRate = PumpProperties().defaultFlowRate

    def setConfig(self, newSetting: float):
        self.defaultPumpFlowRate = newSetting
        setFloatEnvFlag(ConfigurationConstants().defaultFlowRate, newSetting)

    def getConfig(self) -> float:
        return self.defaultPumpFlowRate
