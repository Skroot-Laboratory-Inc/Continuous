import uuid
from urllib import parse

import boto3
import botocore
from botocore.client import Config

import logger
import text_notification


class AwsBoto3:
    def __init__(self, major_version, minor_version):
        config = Config(connect_timeout=5, read_timeout=5)
        self.s3 = boto3.client('s3', config=config)
        self.disabled = False
        self.bucket = 'skroot-data'
        self.dataPrefix = 'data-pdfs/'
        self.dstPdfName = None
        self.newestMajorVersion = major_version
        self.newestMinorVersion = minor_version
        self.newestZipVersion = ''
        try:
            self.folders = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=self.dataPrefix, Delimiter='/')['CommonPrefixes']
        except:
            self.disabled = True
        self.runUuid = uuid.uuid4()
        self.dstLogName = f'error-logs/{self.runUuid}.txt'

    def findFolderAndUploadFile(self, fileLocation, fileType):
        if not self.disabled:
            try:
                for folder in self.folders:
                    try:
                        filename = f'{folder["Prefix"]}{self.runUuid}.pdf'
                        self.s3.upload_file(fileLocation, self.bucket, filename, ExtraArgs={'ContentType': fileType})
                        self.dstPdfName = filename
                        break
                    except botocore.exceptions.ClientError:
                        pass  # This means unauthorized
                    except:
                        logger.exception('Failed to find bucket')
            except botocore.exceptions.EndpointConnectionError:
                logger.info('no internet')
                self.disabled = True
            except:
                logger.exception("Error - most likely there were no folders found in AWS")

    def uploadFile(self, fileLocation, fileName, fileType):
        if not self.disabled:
            text_notification.setText("Uploading file...")
            try:
                tags = {"response_email": "greenwalt@skrootlab.com"}
                self.s3.upload_file(fileLocation, self.bucket, fileName,
                                    ExtraArgs={'ContentType': fileType, "Tagging": parse.urlencode(tags)})
            except botocore.exceptions.EndpointConnectionError:
                logger.info('no internet')
                self.disabled = True
            except:
                logger.exception('Failed to upload file')
                text_notification.setText("Failed to upload file")

    def deleteFile(self, fileName):
        if not self.disabled:
            try:
                self.s3.delete_object(Bucket=self.bucket, Key=fileName)
            except botocore.exceptions.EndpointConnectionError:
                logger.info('no internet')
                self.disabled = True
            except:
                logger.exception('Failed to delete file')

    def checkForSoftwareUpdates(self):
        if not self.disabled:
            updateRequired = False
            filesResult = self.s3.list_objects_v2(Bucket='skroot-data', Prefix="software-releases")
            for item in filesResult['Contents']:
                filename = item['Key']
                if filename == 'software-releases/':
                    continue
                tags = self.s3.get_object_tagging(Bucket='skroot-data', Key=filename)
                majorVersion = float(tags["TagSet"][0]['Value'])
                minorVersion = int(tags["TagSet"][1]['Value'])

                if majorVersion > self.newestMajorVersion or (majorVersion == self.newestMajorVersion and minorVersion > self.newestMinorVersion):
                    self.newestMajorVersion = majorVersion
                    self.newestMinorVersion = minorVersion
                    updateRequired = True
                    self.newestZipVersion = filename

            return f"{self.newestMajorVersion}.{self.newestMinorVersion}", updateRequired
        else:
            return "", False

    def downloadFile(self, aws_filename, local_filename):
        if not self.disabled:
            try:
                self.s3.download_file(self.bucket, aws_filename, local_filename)
            except botocore.exceptions.EndpointConnectionError:
                logger.info('no internet')
                self.disabled = True
            except:
                logger.exception('Failed to download file')

    def downloadSoftwareUpdate(self, local_filename):
        self.downloadFile(self.newestZipVersion, local_filename)