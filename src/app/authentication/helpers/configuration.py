from src.app.authentication.helpers.constants import AuthenticationConstants
from src.app.helper_methods.helper_functions import setBoolEnvFlag, getBoolEnvFlag
from src.app.properties.dev_properties import DevProperties


class AuthConfiguration:
    def __init__(self):
        if not DevProperties().isDevMode:
            self.authenticationEnabled = getBoolEnvFlag(
                AuthenticationConstants().authConfiguration,
                AuthenticationConstants().defaultAuth,
            )
        else:
            self.authenticationEnabled = DevProperties().authEnabled

    def setConfig(self, newSetting: bool):
        self.authenticationEnabled = newSetting
        setBoolEnvFlag(AuthenticationConstants().authConfiguration, newSetting)

    def getConfig(self):
        return self.authenticationEnabled
