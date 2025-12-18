import json
import logging
import os
import platform
from zipfile import ZipFile

import botocore

from src.app.common_modules.aws.aws import AwsBoto3
from src.app.common_modules.aws.helpers.exceptions import DownloadFailedException
from src.app.common_modules.aws.helpers.helpers import runShScript
from src.app.helper_methods.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.helper_methods.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.helper_functions import restartPc
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import release_notes, text_notification
from src.app.widget.confirmation_popup import ConfirmationPopup
from src.resources.version.version import Version


class SoftwareUpdate(AwsBoto3):
    def __init__(self, rootManager: RootManager, major_version, minor_version):
        super().__init__()
        self.newestMajorVersion = major_version
        self.newestMinorVersion = minor_version
        self.RootManager = rootManager
        self.newestZipVersion = ''
        self.releaseNotesPrefix = f'release-notes/{Version().getUseCase()}'
        with open('../resources/version/release-notes.json') as f:
            self.releaseNotes = json.load(f)
        self.CommonFileManager = CommonFileManager()

    def downloadSoftwareUpdate(self):
        try:
            downloadUpdate = self.downloadUpdate(self.CommonFileManager.getTempUpdateZip())
            if downloadUpdate:
                with ZipFile(self.CommonFileManager.getTempUpdateZip(), 'r') as file:
                    file.extractall(path=self.CommonFileManager.getTempSoftwareUpdatePath())
                if platform.system() == "Linux":
                    text_notification.setText(
                        "Installing new dependencies... please wait.\nThis may take up to a minute."
                    )
                    self.RootManager.updateIdleTasks()
                    runShScript(
                        self.CommonFileManager.getTempUpdateScript(),
                        f"{self.CommonFileManager.getExperimentLogDir()}/v{self.newestMajorVersion}.{self.newestMinorVersion}",
                    )
                restartPc()
            else:
                text_notification.setText("Software update aborted.")
        except UserConfirmationException:
            pass
        except:
            logging.exception("failed to update software", extra={"id": "software-update"})

    def checkForSoftwareUpdates(self):
        updateRequired = False
        newestVersion = ""
        if not self.disabled:
            allReleases = self.s3.list_objects_v2(
                Bucket='skroot-data',
                Prefix=f"software-releases/{Version().getUseCase()}",
            )
            # first, we're just going through the releases and finding the most recent one
            most_recent_version = (self.newestMajorVersion, self.newestMinorVersion)
            for item in allReleases['Contents']:
                filename = item['Key']
                majorVersion = 0.0
                minorVersion = 0
                if filename[-1] == '/':
                    continue  # Don't try to get tags of the folder itself
                try:
                    tagsDict = self.s3.get_object_tagging(Bucket='skroot-data', Key=filename)
                    if tagsDict["TagSet"]:
                        for tags in tagsDict["TagSet"]:
                            if tags['Key'] == 'major_version':
                                majorVersion = float(tags['Value'])
                            elif tags['Key'] == 'minor_version':
                                minorVersion = int(tags['Value'])

                except botocore.exceptions.ClientError as e:
                    continue  # This means it's an R&D update, and we are not using an R&D profile
                except:
                    logging.exception("failed to get tags of software update file", extra={"id": "software-update"})
                # find the greatest version in the s3 bucket
                if (most_recent_version[0] < majorVersion) or \
                        (most_recent_version[0] == majorVersion and most_recent_version[1] < minorVersion):
                    most_recent_version = (majorVersion, minorVersion)
                if (self.newestMajorVersion < most_recent_version[0]) or \
                        (self.newestMajorVersion == most_recent_version[0] and self.newestMinorVersion <
                         most_recent_version[1]):
                    updateRequired = True
                    self.updateNewestVersion(majorVersion, minorVersion, filename)
        else:
            return newestVersion, updateRequired
        if not updateRequired:
            text_notification.setText("Software is up to date.")

    def updateNewestVersion(self, majorVersion, minorVersion, filename):
        self.newestMajorVersion = majorVersion
        self.newestMinorVersion = minorVersion
        self.newestZipVersion = filename

    def mergeReleaseNotesIfNeededAndSave(self):
        useCase = Version().getUseCase()
        # Check if this use case exists in release notes structure
        if useCase not in self.releaseNotes:
            self.releaseNotes[useCase] = {}

        # Check if this version exists for the current use case
        if f"v{self.newestMajorVersion}.{self.newestMinorVersion}" not in self.releaseNotes[useCase]:
            localFilename = self.getCurrentReleaseNotes()
            with open(localFilename) as f:
                dictionary = json.load(f)
            # Merge the new version into this use case's release notes
            self.releaseNotes[useCase].update(dictionary)
            os.remove(localFilename)
            with open(f"../resources/version/release-notes.json", "w") as outfile:
                outfile.write(json.dumps(self.releaseNotes, indent=2))

    def getCurrentReleaseNotes(self):
        try:
            localFilename = f"{CommonFileManager().getTempNotes()}/v{self.newestMajorVersion}.{self.newestMinorVersion}.json"
            self.downloadFile(
                f"{self.releaseNotesPrefix}/v{self.newestMajorVersion}.{self.newestMinorVersion}.json",
                localFilename
            )
            return localFilename
        except DownloadFailedException:
            text_notification.setText("Failed to download software update.")

    def downloadUpdate(self, local_filename):
        self.mergeReleaseNotesIfNeededAndSave()
        useCase = Version().getUseCase()
        ReleaseNotes = release_notes.ReleaseNotes(self.releaseNotes, self.RootManager, useCase)
        if ReleaseNotes.download:
            ConfirmationPopup(
                self.RootManager,
                f'Restart Required',
                f'Software update will require the system to restart.\n\nAre you sure you would like to continue?',
            )
            self.downloadFile(self.newestZipVersion, local_filename)
        return ReleaseNotes.download
