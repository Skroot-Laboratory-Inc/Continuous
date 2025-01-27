import datetime
import logging
import os
import uuid
from urllib import parse

import boto3
import botocore
from botocore.client import Config

from src.app.helper.helper_functions import datetimeToMillis
from src.app.model.dynamodbConfig import DynamodbConfig


class AwsBoto3:
    def __init__(self):
        config = Config(connect_timeout=5, read_timeout=5)
        self.s3 = boto3.client('s3', config=config)
        self.dynamodb = boto3.client('dynamodb', config=config)
        self.disabled = False
        self.bucket = 'skroot-data'
        self.dataPrefix = 'experiments/'
        self.runFolder = None
        self.customerId = None
        try:
            self.folders = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.dataPrefix,
                Delimiter='/',
            )['CommonPrefixes']
        except:
            self.disabled = True
        self.runUid = datetimeToMillis(datetime.datetime.now())

    def findFolderAndUploadFile(self, fileLocation, fileType, tags):
        """ Internal use only to upload the first file of a folder. """
        if not self.disabled:
            for folder in self.folders:
                try:
                    self.s3.upload_file(
                        fileLocation,
                        self.bucket,
                        f'{folder["Prefix"]}{self.runUid}/{os.path.basename(fileLocation)}',
                        ExtraArgs={'ContentType': fileType, "Tagging": parse.urlencode(tags),
                                   "CacheControl": "no-cache"})
                    self.customerId = str(folder["Prefix"]).split('/')[-2]
                    self.runFolder = f'{folder["Prefix"]}{self.runUid}'
                    break
                except Exception as e:
                    if type(e.__context__) is botocore.exceptions.ClientError:
                        pass  # This means unauthorized
                    else:
                        raise

    def uploadFile(self, fileLocation, fileType, tags={}, subDir=None) -> bool:
        if not self.disabled:
            try:
                if not self.runFolder:
                    self.findFolderAndUploadFile(fileLocation, fileType, tags)
                else:
                    destination = f'{self.runFolder}/{os.path.basename(fileLocation)}'
                    if subDir:
                        destination = f'{destination}/{subDir}'
                    self.s3.upload_file(
                        fileLocation, self.bucket, destination,
                        ExtraArgs={'ContentType': fileType,
                                   "Tagging": parse.urlencode(tags),
                                   "CacheControl": "no-cache"})
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet', extra={"id": "aws"})
                return False
            except:
                logging.exception('Error - most likely there were no folders found in AWS.', extra={"id": "aws"})
                return False
            return True
        else:
            return False

    def downloadFile(self, aws_filename, local_filename):
        if not self.disabled:
            try:
                self.s3.download_file(self.bucket, aws_filename, local_filename)
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet', extra={"id": "aws"})
                self.disabled = True
            except:
                pass

    def pushExperimentRow(self, config: DynamodbConfig) -> bool:
        if not self.disabled:
            if self.customerId is not None:
                self.dynamodb.put_item(
                    TableName='runs',
                    Item={
                        'customerId': {'S': self.customerId},
                        'runUid': {'N': str(self.runUid)},
                        'startDate': {'N': str(config.startDate)},
                        'endDate': {'S': str(config.endDate)},
                        'saturationDate': {'S': config.saturationDate},
                        'incubator': {'S': config.incubator},
                        'lotId': {'S': config.lotId},
                        'automatedFlagged': {'BOOL': config.flagged},
                    }
                )
                return True
        return False
