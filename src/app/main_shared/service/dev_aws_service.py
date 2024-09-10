from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.properties.dev_properties import DevProperties
from src.app.ui_manager.root_manager import RootManager
from src.app.main_shared.service.aws_service import AwsService


class DevAwsService(AwsService):
    def __init__(self, rootManager: RootManager, major_version, minor_version, globalFileManager: GlobalFileManager):
        super().__init__(rootManager, major_version, minor_version, globalFileManager)

        # This makes the app act as if it is not connected to the internet.
        properties = DevProperties()
        self.SoftwareUpdate.disabled = properties.disableAws
        self.AwsBoto3Service.disabled = properties.disableAws
