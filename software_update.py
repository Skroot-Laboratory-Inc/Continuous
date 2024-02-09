import json
import logging
import os

import botocore

import release_notes
from aws import AwsBoto3


class SoftwareUpdate(AwsBoto3):
    def __init__(self, root, major_version, minor_version, location):
        super().__init__()
        self.newestMajorVersion = major_version
        self.newestMinorVersion = minor_version
        self.location = location
        self.root = root
        self.newestZipVersion = ''
        self.releaseNotesPrefix = 'release-notes'
        with open('./resources/release-notes.json') as f:
            self.releaseNotes = json.load(f)

    def getCurrentReleaseNotes(self):
        localFilename = f"{self.location}/v{self.newestMajorVersion}.{self.newestMinorVersion}.json"
        self.downloadFile(
            f"{self.releaseNotesPrefix}/v{self.newestMajorVersion}.{self.newestMinorVersion}.json",
            localFilename
        )
        return localFilename

    def mergeReleaseNotesIfNeededAndSave(self):
        if f"v{self.newestMajorVersion}.{self.newestMinorVersion}" not in self.releaseNotes:
            localFilename = self.getCurrentReleaseNotes()
            with open(localFilename) as f:
                dictionary = json.load(f)
            self.releaseNotes.update(dictionary)
            os.remove(localFilename)
            with open(f"./resources/release-notes.json", "w") as outfile:
                outfile.write(json.dumps(self.releaseNotes))

    def downloadSoftwareUpdate(self, local_filename):
        self.mergeReleaseNotesIfNeededAndSave()
        ReleaseNotes = release_notes.ReleaseNotes(self.releaseNotes, self.root)
        if ReleaseNotes.download:
            self.downloadFile(self.newestZipVersion, local_filename)
        return ReleaseNotes.download

    def checkForSoftwareUpdates(self):
        if not self.disabled:
            allReleases = self.s3.list_objects_v2(Bucket='skroot-data', Prefix="software-releases")
            for item in allReleases['Contents']:
                filename = item['Key']
                if filename == 'software-releases/':
                    continue  # Don't try to get tags of the folder itself
                try:
                    tags = self.s3.get_object_tagging(Bucket='skroot-data', Key=filename)
                    majorVersion = float(tags["TagSet"][0]['Value'])
                    minorVersion = int(tags["TagSet"][1]['Value'])
                except botocore.exceptions.ClientError:
                    continue  # This means it's an R&D update and we are not using an R&D profile
                except:
                    logging.exception("failed to get tags of software update file")
                if majorVersion > self.newestMajorVersion or (
                        majorVersion == self.newestMajorVersion and minorVersion > self.newestMinorVersion):
                    self.updateNewestVersion(majorVersion, minorVersion, filename)
                    return f"{self.newestMajorVersion}.{self.newestMinorVersion}", True
            return f"{self.newestMajorVersion}.{self.newestMinorVersion}", False
        else:
            return "", False

    def updateNewestVersion(self, majorVersion, minorVersion, filename):
        self.newestMajorVersion = majorVersion
        self.newestMinorVersion = minorVersion
        self.newestZipVersion = filename
