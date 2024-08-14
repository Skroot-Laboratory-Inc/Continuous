import logging
import shutil
from zipfile import ZipFile

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.helper import helper_functions
from src.app.helper.helper_functions import getOperatingSystem
from src.app.main_shared.service.aws_service_interface import AwsServiceInterface
from src.app.main_shared.service.software_update import SoftwareUpdate
from src.app.properties.properties import CommonProperties
from src.app.widget import text_notification


class AwsService(AwsServiceInterface):
    def __init__(self, root, major_version, minor_version, globalFileManager: GlobalFileManager):
        self.SoftwareUpdate = SoftwareUpdate(root, major_version, minor_version)
        self.CommonFileManager = CommonFileManager()
        self.Properties = CommonProperties()
        self.awsTimeBetweenUploads = self.Properties.awsTimeBetweenUploads
        self.GlobalFileManager = globalFileManager
        self.awsLastUploadTime = 0

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
                    file.extractall()
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

    def uploadSummaryPdf(self, scanNumber):
        if not self.SoftwareUpdate.disabled:
            if self.SoftwareUpdate.dstPdfName is None:
                self.SoftwareUpdate.findFolderAndUploadFile(self.GlobalFileManager.getSummaryPdf(), "application/pdf")
            else:
                if (scanNumber - self.awsLastUploadTime) > self.awsTimeBetweenUploads:
                    self.SoftwareUpdate.uploadFile(self.GlobalFileManager.getSummaryPdf(),
                                                   self.SoftwareUpdate.dstPdfName,
                                                   'application/pdf')
                    self.awsLastUploadTime = scanNumber

    def uploadExperimentLog(self):
        if not self.SoftwareUpdate.disabled:
            self.SoftwareUpdate.uploadFile(
                self.CommonFileManager.getExperimentLog(),
                self.SoftwareUpdate.dstLogName,
                'text/plain',
            )
            return True
        return False
