from src.app.helper_methods.configuration_constants import ConfigurationConstants
from src.app.helper_methods.helper_functions import setStringEnvFlag, getStringEnvFlag
from src.app.properties.dev_properties import DevProperties


class WarehouseConfiguration:
    def __init__(self):
        if not DevProperties().isDevMode:
            self.warehouse = getStringEnvFlag(
                ConfigurationConstants().warehouse,
                "",
            )
        else:
            self.warehouse = ""

    def setConfig(self, newSetting: str):
        self.warehouse = newSetting
        setStringEnvFlag(ConfigurationConstants().warehouse, newSetting)

    def getConfig(self):
        return self.warehouse
