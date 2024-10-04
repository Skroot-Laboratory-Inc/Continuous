import os
from datetime import datetime

from src.app.aws.aws import AwsBoto3
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import datetimeToMillis
from src.app.reader.service.aws_service_interface import AwsServiceInterface
from src.app.model.guided_setup_input import GuidedSetupInput
from src.app.properties.aws_properties import AwsProperties


class AwsService(AwsServiceInterface):
    def __init__(self, readerFileManager: ReaderFileManager, globalFileManager: GlobalFileManager):
        self.AwsBoto3Service = AwsBoto3()
        self.CommonFileManager = CommonFileManager()
        self.AwsProperties = AwsProperties()
        self.csvUploadRate = self.AwsProperties.csvUploadRate
        self.notesUploadRate = self.AwsProperties.notesUploadRate
        self.ReaderFileManager = readerFileManager
        self.GlobalFileManager = globalFileManager
        self.awsLastCsvUploadTime = 100001
        self.awsLastNotesUploadTime = 100001

    def uploadExperimentFilesOnInterval(self, scanNumber, guidedSetupForm: GuidedSetupInput):
        self.uploadReaderCsvOnInterval(scanNumber, guidedSetupForm)

    def uploadReaderCsvOnInterval(self, scanNumber, guidedSetupForm: GuidedSetupInput):
        if (scanNumber - self.awsLastCsvUploadTime) >= self.csvUploadRate:
            self.AwsBoto3Service.uploadFile(
                self.ReaderFileManager.getSmoothAnalyzed(),
                "text/csv",
                tags={
                    "end_date": None,
                    "start_date": guidedSetupForm.getDateMillis(),
                    "lot_id": guidedSetupForm.getLotId(),
                    "incubator": guidedSetupForm.getIncubator(),
                    "scan_rate": guidedSetupForm.getScanRate(),
                },
            )
            self.awsLastCsvUploadTime = scanNumber

    def uploadFinalExperimentFiles(self, guidedSetupForm: GuidedSetupInput):
        self.AwsBoto3Service.uploadFile(
            self.ReaderFileManager.getSmoothAnalyzed(),
            "text/csv",
            tags={
                "end_date": datetimeToMillis(datetime.now()),
                "start_date": guidedSetupForm.getDateMillis(),
                "lot_id": guidedSetupForm.getLotId(),
                "incubator": guidedSetupForm.getIncubator(),
                "scan_rate": guidedSetupForm.getScanRate(),
            },
        )

    def uploadIssueLog(self):
        return self.AwsBoto3Service.uploadFile(
            self.GlobalFileManager.getIssueLog(),
            'application/json'
        )

    def downloadIssueLogIfModified(self, lastDownloaded):
        lastModified = self.AwsBoto3Service.getLastModified(
            f'{self.AwsBoto3Service.runFolder}/{os.path.basename(self.GlobalFileManager.getIssueLog())}',
        )
        if lastModified > lastDownloaded:
            self.downloadIssueLog()
            return lastModified
        return lastDownloaded

    def downloadIssueLog(self):
        return self.AwsBoto3Service.downloadFile(
            f'{self.AwsBoto3Service.runFolder}/{os.path.basename(self.GlobalFileManager.getIssueLog())}',
            self.GlobalFileManager.getIssueLog(),
        )

