from src.app.common_modules.service.software_update import SoftwareUpdate
from src.app.properties.dev_properties import DevProperties
from src.app.ui_manager.root_manager import RootManager


class DevSoftwareUpdate(SoftwareUpdate):
    def __init__(self, rootManager: RootManager, major_version, minor_version):
        super().__init__(rootManager, major_version, minor_version)

        # This makes the app act as if it is not connected to the internet.
        properties = DevProperties()
        self.disabled = properties.disableAws
