from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.reader.service.aws_service import AwsService
from src.app.properties.dev_properties import DevProperties


class DevAwsService(AwsService):
    def __init__(self, readerFileManager: ReaderFileManager, globalFileManager: GlobalFileManager):
        super().__init__(readerFileManager, globalFileManager)

        # This makes the app act as if it is not connected to the internet.
        properties = DevProperties()
        self.AwsBoto3Service.disabled = properties.disableAws
