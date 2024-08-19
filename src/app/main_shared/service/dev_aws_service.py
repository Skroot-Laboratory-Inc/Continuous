from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.main_shared.service.aws_service import AwsService


class DevAwsService(AwsService):
    def __init__(self, root, major_version, minor_version, globalFileManager: GlobalFileManager):
        super().__init__(root, major_version, minor_version, globalFileManager)

        # This makes the app act as if it is not connected to the internet.
        self.SoftwareUpdate.disabled = True
