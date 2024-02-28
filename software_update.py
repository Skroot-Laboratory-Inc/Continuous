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
        # if our current newest version is less than that, then we'll update it and return True
        out_of_date = False
        if not self.disabled:
            allReleases = self.s3.list_objects_v2(Bucket='skroot-data', Prefix="software-releases")
            # first, we're just going through the releases and finding the most recent one
            most_recent_version = (self.newestMajorVersion, self.newestMinorVersion)
            for item in allReleases['Contents']:
                filename = item['Key']
                if filename == 'software-releases/':
                    continue  # Don't try to get tags of the folder itself
                try:
                    tags = self.s3.get_object_tagging(Bucket='skroot-data', Key=filename)
                    if tags["TagSet"] != []:
                        majorVersion = float(tags["TagSet"][0]['Value'])
                        minorVersion = int(tags["TagSet"][1]['Value'])
                    else:
                        # We are looking at an untagged item, likely a folder.
                        majorVersion = 0.0
                        minorVersion = 0
                except botocore.exceptions.ClientError:
                    continue  # This means it's an R&D update and we are not using an R&D profile
                except:
                    logging.exception("failed to get tags of software update file")
                # find the greatest version in the s3 bucket
                if (most_recent_version[0] < majorVersion) or \
                        (most_recent_version[0] == majorVersion and most_recent_version[1] < minorVersion):
                    most_recent_version = (majorVersion, minorVersion)
                if (self.newestMajorVersion < most_recent_version[0]) or \
                        (self.newestMajorVersion == most_recent_version[0] and self.newestMinorVersion < most_recent_version[1]):
                    out_of_date = True
                    self.updateNewestVersion(majorVersion, minorVersion, filename)
            return f"{most_recent_version[0]}.{most_recent_version[1]}", out_of_date
        else:
            return "", False

    def updateNewestVersion(self, majorVersion, minorVersion, filename):
        self.newestMajorVersion = majorVersion
        self.newestMinorVersion = minorVersion
        self.newestZipVersion = filename
