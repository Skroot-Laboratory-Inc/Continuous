import os
from datetime import datetime

from src.app.aws.aws import AwsBoto3
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import datetimeToMillis, datetimeToDisplay
from src.app.model.dynamodbConfig import DynamodbConfig
from src.app.reader.service.aws_service_interface import AwsServiceInterface
from src.app.model.setup_reader_form_input import SetupReaderFormInput
from src.app.properties.aws_properties import AwsProperties


class AwsService(AwsServiceInterface):
    def __init__(self, readerFileManager: ReaderFileManager, globalFileManager: GlobalFileManager):
        self.AwsBoto3Service = AwsBoto3()
        self.currentDynamodbConfig = DynamodbConfig()
        self.CommonFileManager = CommonFileManager()
        self.AwsProperties = AwsProperties()
        self.csvUploadRate = self.AwsProperties.csvUploadRate
        self.rawDataUploadRate = self.AwsProperties.rawDataUploadRate
        self.notesUploadRate = self.AwsProperties.notesUploadRate
        self.ReaderFileManager = readerFileManager
        self.GlobalFileManager = globalFileManager
        self.awsLastCsvUploadTime = 100000
        self.awsLastRawDataUploadTime = 100000
        self.awsLastNotesUploadTime = 100000

    def uploadExperimentFilesOnInterval(self, scanNumber, guidedSetupForm: SetupReaderFormInput, saturationDate: datetime, flagged: bool):
        newConfig = DynamodbConfig(None,
                                   guidedSetupForm.getDateMillis(),
                                   saturationDate,
                                   guidedSetupForm.getLotId(),
                                   guidedSetupForm.getIncubator(),
                                   flagged)
        self.uploadReaderCsvOnInterval(scanNumber, newConfig)
        self.uploadRawDataOnInterval(scanNumber)

    def uploadReaderCsvOnInterval(self, scanNumber, newConfig: DynamodbConfig):
        if (scanNumber - self.awsLastCsvUploadTime) >= self.csvUploadRate:
            self.uploadReaderAnalyzed(newConfig)
            self.awsLastCsvUploadTime = scanNumber
            if self.currentDynamodbConfig != newConfig:
                if self.AwsBoto3Service.pushExperimentRow(newConfig):
                    self.currentDynamodbConfig = newConfig
        else:
            if not self.currentDynamodbConfig.softEquals(newConfig):
                if self.AwsBoto3Service.pushExperimentRow(newConfig):
                    self.currentDynamodbConfig = newConfig

    def uploadRawDataOnInterval(self, scanNumber):
        if (scanNumber - self.awsLastRawDataUploadTime) >= self.rawDataUploadRate:
            self.AwsBoto3Service.uploadFile(
                self.ReaderFileManager.getCurrentScan(),
                "text/csv",
            )
            self.awsLastRawDataUploadTime = scanNumber

    def uploadFinalExperimentFiles(self, guidedSetupForm: SetupReaderFormInput, saturationDate: datetime):
        newConfig = DynamodbConfig(datetimeToMillis(datetime.now()),
                                   guidedSetupForm.getDateMillis(),
                                   saturationDate,
                                   guidedSetupForm.getLotId(),
                                   guidedSetupForm.getIncubator(),
                                   False)
        self.uploadReaderAnalyzed(newConfig)
        self.AwsBoto3Service.pushExperimentRow(newConfig)

    def uploadReaderAnalyzed(self, config: DynamodbConfig):
        self.AwsBoto3Service.uploadFile(
            self.ReaderFileManager.getSmoothAnalyzed(),
            "text/csv",
            tags=config.asTags(),
        )

    def uploadIssueLog(self):
        return self.AwsBoto3Service.uploadFile(
            self.GlobalFileManager.getIssueLog(),
            'application/json'
        )
