import logging
import os
import uuid
from urllib import parse

import boto3
import botocore
from botocore.client import Config


class AwsBoto3:
    def __init__(self):
        config = Config(connect_timeout=5, read_timeout=5)
        self.s3 = boto3.client('s3', config=config)
        self.disabled = False
        self.bucket = 'skroot-data'
        self.dataPrefix = 'experiments/'
        self.runFolder = None
        try:
            self.folders = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.dataPrefix,
                Delimiter='/',
            )['CommonPrefixes']
        except:
            self.disabled = True
        self.runUuid = uuid.uuid4()

    def findFolderAndUploadFile(self, fileLocation, fileType, tags):
        if not self.disabled:
            for folder in self.folders:
                try:
                    self.s3.upload_file(
                        fileLocation,
                        self.bucket,
                        f'{folder["Prefix"]}{self.runUuid}/{os.path.basename(fileLocation)}',
                        ExtraArgs={'ContentType': fileType, "Tagging": parse.urlencode(tags)})
                    self.runFolder = f'{folder["Prefix"]}{self.runUuid}'
                    break
                except Exception as e:
                    if type(e.__context__) is botocore.exceptions.ClientError:
                        pass  # This means unauthorized
                    else:
                        logging.exception('Failed to find a bucket that the user is authorized for.')
                        raise

    def uploadFile(self, fileLocation, fileType, tags) -> bool:
        if not self.disabled:
            try:
                if not self.runFolder:
                    self.findFolderAndUploadFile(fileLocation, fileType, tags)
                else:
                    self.s3.upload_file(
                        fileLocation,
                        self.bucket,
                        f'{self.runFolder}/{os.path.basename(fileLocation)}',
                        ExtraArgs={'ContentType': fileType, "Tagging": parse.urlencode(tags)})
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet')
                self.disabled = True
                return False
            except:
                logging.exception('Error - most likely there were no folders found in AWS.')
                return False
            return True
        else:
            return False

    def deleteFile(self, fileName):
        if not self.disabled:
            try:
                self.s3.delete_object(Bucket=self.bucket, Key=fileName)
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet')
                self.disabled = True
            except:
                logging.exception('Failed to delete file')

    def downloadFile(self, aws_filename, local_filename):
        if not self.disabled:
            try:
                self.s3.download_file(self.bucket, aws_filename, local_filename)
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet')
                self.disabled = True
            except:
                logging.exception('Failed to download file')
