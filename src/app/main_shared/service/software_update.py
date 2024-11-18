import json
import logging
import os
import shutil
from zipfile import ZipFile

import botocore

from src.app.aws.aws import AwsBoto3
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.root_manager import RootManager
from src.app.helper.helper_functions import getCwd, getOperatingSystem, runShScript, confirmAndPowerDown, shouldRestart, \
    restart
from src.app.widget import release_notes, text_notification
from src.resources.version import Version


class SoftwareUpdate(AwsBoto3):
    def __init__(self, rootManager: RootManager, major_version, minor_version):
        super().__init__()
        self.newestMajorVersion = major_version
        self.newestMinorVersion = minor_version
        self.RootManager = rootManager
        self.newestZipVersion = ''
        self.releaseNotesPrefix = f'release-notes/{Version().getUseCase()}'
        with open('../resources/release-notes-manufacturing.json') as f:
            self.releaseNotes = json.load(f)
        self.CommonFileManager = CommonFileManager()

    def downloadSoftwareUpdate(self):
        try:
            downloadUpdate = self.downloadUpdate(self.CommonFileManager.getTempUpdateFile())
            if downloadUpdate:
                with ZipFile(self.CommonFileManager.getTempUpdateFile(), 'r') as file:
                    file.extractall(path=self.CommonFileManager.getSoftwareUpdatePath())
                if getOperatingSystem() == "linux":
                    shutil.copyfile(self.CommonFileManager.getLocalDesktopFile(),
                                    self.CommonFileManager.getRemoteDesktopFile())
                    text_notification.setText(
                        "Installing new dependencies... please wait. This may take up to a minute.")
                    self.RootManager.updateIdleTasks()
                    runShScript(
                        self.CommonFileManager.getInstallScript(),
                        self.CommonFileManager.getExperimentLog(),
                    )
                text_notification.setText(
                    f"New software version updated v{self.newestMajorVersion}.{self.newestMinorVersion}")
                self.RootManager.updateIdleTasks()
                restart()
            else:
                text_notification.setText("Software update aborted.")
        except:
            logging.exception("failed to update software", extra={"id": "software-update"})

    def checkForSoftwareUpdates(self):
        updateRequired = False
        newestVersion = ""
        if not self.disabled:
            allReleases = self.s3.list_objects_v2(Bucket='skroot-data', Prefix="software-releases")
            # first, we're just going through the releases and finding the most recent one
            most_recent_version = (self.newestMajorVersion, self.newestMinorVersion)
            for item in allReleases['Contents']:
                filename = item['Key']
                if filename == 'software-releases/':
                    continue  # Don't try to get tags of the folder itself
                try:
                    tagsDict = self.s3.get_object_tagging(Bucket='skroot-data', Key=filename)
                    if tagsDict["TagSet"]:
                        for tags in tagsDict["TagSet"]:
                            if tags['Key'] == 'major_version':
                                majorVersion = float(tags['Value'])
                            elif tags['Key'] == 'minor_version':
                                minorVersion = int(tags['Value'])
                    else:
                        # We are looking at an untagged item, likely a folder.
                        majorVersion = 0.0
                        minorVersion = 0
                except botocore.exceptions.ClientError:
                    continue  # This means it's an R&D update, and we are not using an R&D profile
                except:
                    logging.exception("failed to get tags of software update file", extra={"id": "software-update"})
                # find the greatest version in the s3 bucket
                if (most_recent_version[0] < majorVersion) or \
                        (most_recent_version[0] == majorVersion and most_recent_version[1] < minorVersion):
                    most_recent_version = (majorVersion, minorVersion)
                if (self.newestMajorVersion < most_recent_version[0]) or \
                        (self.newestMajorVersion == most_recent_version[0] and self.newestMinorVersion < most_recent_version[1]):
                    updateRequired = True
                    self.updateNewestVersion(majorVersion, minorVersion, filename)
            newestVersion = f"{most_recent_version[0]}.{most_recent_version[1]}"
        else:
            return newestVersion, updateRequired
        if updateRequired:
            text_notification.setText(
                f"Newer software available v{newestVersion} consider upgrading to use new features")

    def updateNewestVersion(self, majorVersion, minorVersion, filename):
        self.newestMajorVersion = majorVersion
        self.newestMinorVersion = minorVersion
        self.newestZipVersion = filename

    def mergeReleaseNotesIfNeededAndSave(self):
        if f"v{self.newestMajorVersion}.{self.newestMinorVersion}" not in self.releaseNotes:
            localFilename = self.getCurrentReleaseNotes()
            with open(localFilename) as f:
                dictionary = json.load(f)
            self.releaseNotes.update(dictionary)
            os.remove(localFilename)
            with open(f"../resources/release-notes-manufacturing.json", "w") as outfile:
                outfile.write(json.dumps(self.releaseNotes))

    def getCurrentReleaseNotes(self):
        localFilename = f"{getCwd()}/v{self.newestMajorVersion}.{self.newestMinorVersion}.json"
        self.downloadFile(
            f"{self.releaseNotesPrefix}/v{self.newestMajorVersion}.{self.newestMinorVersion}.json",
            localFilename
        )
        return localFilename

    def downloadUpdate(self, local_filename):
        self.mergeReleaseNotesIfNeededAndSave()
        ReleaseNotes = release_notes.ReleaseNotes(self.releaseNotes, self.RootManager)
        if ReleaseNotes.download:
            confirmRestart = shouldRestart()
            if confirmRestart:
                self.downloadFile(self.newestZipVersion, local_filename)
            return confirmRestart
        return ReleaseNotes.download
