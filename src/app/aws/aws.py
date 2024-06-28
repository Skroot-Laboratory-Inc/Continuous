import json
import logging
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
        self.dataPrefix = 'data-pdfs/'
        self.dstPdfName = None
        try:
            self.folders = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=self.dataPrefix, Delimiter='/')[
                'CommonPrefixes']
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
                    except Exception as e:
                        if type(e.__context__) is botocore.exceptions.ClientError:
                            pass  # This means unauthorized
                        else:
                            logging.exception('Failed to find bucket')
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet')
                self.disabled = True
            except:
                logging.exception("Error - most likely there were no folders found in AWS")

    def uploadFile(self, fileLocation, fileName, fileType):
        if not self.disabled:
            try:
                tags = {"response_email": "greenwalt@skrootlab.com"}
                self.s3.upload_file(fileLocation, self.bucket, fileName,
                                    ExtraArgs={'ContentType': fileType, "Tagging": parse.urlencode(tags)})
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet')
                self.disabled = True
            except:
                logging.exception('Failed to upload file')

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