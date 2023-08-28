import uuid

import boto3
import botocore
from botocore.client import Config

import logger


class AwsBoto3:
    def __init__(self):
        config = Config(connect_timeout=5, read_timeout=5)
        self.s3 = boto3.client('s3', config=config)
        self.disabled = True
        self.bucket = 'skroot-data'
        self.dstPdfName = None
        self.dstPdfName = None
        try:
            self.folders = self.s3.list_objects_v2(Bucket='skroot-data', Delimiter='/')['CommonPrefixes']
        except:
            self.disabled = True

    def findFolder(self, fileLocation):
        try:
            for folder in self.folders:
                try:
                    filename = f'{folder["Prefix"]}{uuid.uuid4()}.pdf'
                    self.s3.upload_file(fileLocation, self.bucket, filename)
                    self.dstPdfName = filename
                    break
                except botocore.exceptions.ClientError:
                    pass  # This means unauthorized
                except:
                    logger.exception('Failed to find bucket')
        except botocore.exceptions.EndpointConnectionError:
            logger.info('no internet')
            self.disabled = True

    def uploadFile(self, fileLocation):
        if self.dstPdfName is None:
            self.findFolder(fileLocation)
        if not self.disabled:
            try:
                self.s3.upload_file(fileLocation, self.bucket, self.dstPdfName,
                                    ExtraArgs={'ContentType': 'application/pdf', 'ContentDisposition': 'inline'})
            except botocore.exceptions.EndpointConnectionError:
                logger.info('no internet')
                self.disabled = True
            except:
                logger.exception('Failed to upload file')

    def downloadFile(self, filename):
        if not self.disabled:
            try:
                self.s3.download_file(self.bucket, filename, filename)
            except botocore.exceptions.EndpointConnectionError:
                logger.info('no internet')
                self.disabled = True
            except:
                logger.exception('Failed to download file')
