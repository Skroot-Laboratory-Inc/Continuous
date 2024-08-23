import logging
import shutil
from datetime import datetime
from zipfile import ZipFile

from src.app.aws.aws import AwsBoto3
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.helper import helper_functions
from src.app.helper.helper_functions import getOperatingSystem
from src.app.main_shared.service.aws_service_interface import AwsServiceInterface
from src.app.main_shared.service.software_update import SoftwareUpdate
from src.app.model.guided_setup_input import GuidedSetupInput
from src.app.properties.aws_properties import AwsProperties
from src.app.widget import text_notification


class AwsService(AwsServiceInterface):
    def __init__(self, root, major_version, minor_version, globalFileManager: GlobalFileManager):
        self.SoftwareUpdate = SoftwareUpdate(root, major_version, minor_version)
        self.AwsBoto3Service = AwsBoto3()
        self.CommonFileManager = CommonFileManager()
        self.AwsProperties = AwsProperties()
        self.csvUploadRate = self.AwsProperties.csvUploadRate
        self.notesUploadRate = self.AwsProperties.notesUploadRate
        self.GlobalFileManager = globalFileManager
        self.awsLastCsvUploadTime = 100001
        self.awsLastNotesUploadTime = 100001

    def checkForSoftwareUpdate(self):
        newestVersion, updateRequired = self.SoftwareUpdate.checkForSoftwareUpdates()
        if updateRequired:
            text_notification.setText(
                f"Newer software available v{newestVersion} consider upgrading to use new features")

    def downloadSoftwareUpdate(self):
        try:
            downloadUpdate = self.SoftwareUpdate.downloadSoftwareUpdate(self.CommonFileManager.getTempUpdateFile())
            if downloadUpdate:
                with ZipFile(self.CommonFileManager.getTempUpdateFile(), 'r') as file:
                    file.extractall(path=self.CommonFileManager.getSoftwareUpdatePath())
                if getOperatingSystem() == "linux":
                    shutil.copyfile(self.CommonFileManager.getLocalDesktopFile(),
                                    self.CommonFileManager.getRemoteDesktopFile())
                    text_notification.setText(
                        "Installing new dependencies... please wait. This may take up to a minute.")
                    helper_functions.runShScript(self.CommonFileManager.getInstallScript(),
                                                 self.CommonFileManager.getExperimentLog())
                text_notification.setText(
                    f"New software version updated v{self.SoftwareUpdate.newestMajorVersion}.{self.SoftwareUpdate.newestMinorVersion}")
            else:
                text_notification.setText("Software update aborted.")
        except:
            logging.exception("failed to update software")

    def uploadExperimentFilesOnInterval(self, scanNumber, guidedSetupForm: GuidedSetupInput):
        self.uploadSummaryCsvOnInterval(scanNumber, guidedSetupForm)
        self.uploadExperimentNotesOnInterval(scanNumber, guidedSetupForm)

    def uploadSummaryCsvOnInterval(self, scanNumber, guidedSetupForm: GuidedSetupInput):
        if (scanNumber - self.awsLastCsvUploadTime) >= self.csvUploadRate:
            self.AwsBoto3Service.uploadFile(
                self.GlobalFileManager.getSummaryAnalyzed(),
                "text/csv",
                tags={
                    "end_date": None,
                    "start_date": guidedSetupForm.getDate(),
                    "experiment_id": guidedSetupForm.getExperimentId(),
                    "scan_rate": guidedSetupForm.getScanRate(),
                    "num_readers": guidedSetupForm.getNumReaders(),
                }
            )
            self.awsLastCsvUploadTime = scanNumber

    def uploadExperimentNotesOnInterval(self, scanNumber, guidedSetupForm: GuidedSetupInput):
        if (scanNumber - self.awsLastNotesUploadTime) >= self.notesUploadRate:
            self.AwsBoto3Service.uploadFile(
                self.GlobalFileManager.getExperimentMetadata(),
                "application/json",
                tags={
                    "experiment_id": guidedSetupForm.getExperimentId(),
                }
            )
            self.awsLastNotesUploadTime = scanNumber

    def uploadFinalExperimentFiles(self, guidedSetupForm: GuidedSetupInput):
        currentDate = datetime.now().date()
        self.AwsBoto3Service.uploadFile(
            self.GlobalFileManager.getSummaryAnalyzed(),
            "text/csv",
            tags={
                "end_date": f'{currentDate.month}-{currentDate.day}-{currentDate.year}',
                "start_date": guidedSetupForm.getDate(),
                "experiment_id": guidedSetupForm.getExperimentId(),
                "scan_rate": guidedSetupForm.getScanRate(),
                "num_readers": guidedSetupForm.getNumReaders(),
            }
        )


    def uploadExperimentLog(self):
        return self.AwsBoto3Service.uploadFile(
            self.CommonFileManager.getExperimentLog(),
            'text/plain',
            tags={"response_email": "greenwalt@skrootlab.com"}
        )
