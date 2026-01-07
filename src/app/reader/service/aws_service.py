import socket
from datetime import datetime

from src.app.common_modules.aws.aws import AwsBoto3
from src.app.helper_methods.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.file_manager.global_file_manager import GlobalFileManager
from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.helper_methods.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.model.dynamodbConfig import DynamodbConfig
from src.app.properties.aws_properties import AwsProperties


class AwsService:
    def __init__(self, readerFileManager: ReaderFileManager, globalFileManager: GlobalFileManager):
        self.AwsBoto3Service = AwsBoto3()
        self.currentDynamodbConfig = DynamodbConfig()
        self.CommonFileManager = CommonFileManager()
        self.AwsProperties = AwsProperties()
        self.csvUploadRate = self.AwsProperties.csvUploadRate * 60000
        self.rawDataUploadRate = self.AwsProperties.rawDataUploadRate * 60000
        self.notesUploadRate = self.AwsProperties.notesUploadRate * 60000
        self.ReaderFileManager = readerFileManager
        self.GlobalFileManager = globalFileManager
        self.awsLastCsvUploadMillis = datetimeToMillis(datetime.now())
        self.awsLastRawDataUploadMillis = datetimeToMillis(datetime.now())
        self.awsLastNotesUploadMillis = datetimeToMillis(datetime.now())

    def uploadExperimentFilesOnInterval(self, scanMillis: int, lotId: str, saturationDate: int, flagged: bool, startDate: int, warehouse: str = ""):
        newConfig = DynamodbConfig(None,
                                   startDate,
                                   saturationDate,
                                   lotId,
                                   socket.gethostname(),
                                   flagged,
                                   warehouse)
        self.uploadReaderCsvOnInterval(scanMillis, newConfig)
        self.uploadRawDataOnInterval(scanMillis)

    def uploadReaderCsvOnInterval(self, scanMillis, newConfig: DynamodbConfig):
        if (scanMillis - self.awsLastCsvUploadMillis) >= self.csvUploadRate:
            self.uploadReaderAnalyzed(newConfig)
            self.awsLastCsvUploadMillis = scanMillis
            if self.AwsBoto3Service.pushExperimentRow(newConfig):
                self.currentDynamodbConfig = newConfig
        else:
            if not self.currentDynamodbConfig.softEquals(newConfig):
                if self.AwsBoto3Service.pushExperimentRow(newConfig):
                    self.currentDynamodbConfig = newConfig

    def uploadRawDataOnInterval(self, scanMillis):
        if (scanMillis - self.awsLastRawDataUploadMillis) >= self.rawDataUploadRate:
            self.AwsBoto3Service.uploadFile(
                self.ReaderFileManager.getCurrentScan(),
                "text/csv",
            )
            self.awsLastRawDataUploadMillis = scanMillis

    def uploadFinalExperimentFiles(self, lotId: str, saturationDate: int, startDate: int, warehouse: str = ""):
        newConfig = DynamodbConfig(datetimeToMillis(datetime.now()),
                                   startDate,
                                   saturationDate,
                                   lotId,
                                   socket.gethostname(),
                                   False,
                                   warehouse)
        self.uploadReaderAnalyzed(newConfig)
        self.AwsBoto3Service.pushExperimentRow(newConfig)

    def uploadReaderAnalyzed(self, config: DynamodbConfig):
        self.AwsBoto3Service.uploadFile(
            self.ReaderFileManager.getSmoothAnalyzed(),
            "text/csv",
            tags=config.asTags(),
        )

    def uploadSecondAxis(self):
        return self.AwsBoto3Service.uploadFile(
            self.ReaderFileManager.getSecondAxis(),
            'text/csv'
        )

    def uploadIssueLog(self):
        return self.AwsBoto3Service.uploadFile(
            self.GlobalFileManager.getIssueLog(),
            'application/json'
        )
