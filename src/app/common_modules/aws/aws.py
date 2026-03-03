import datetime
import logging
import os
from urllib import parse

import boto3
import botocore
from botocore.client import Config
from src.app.common_modules.aws.device_credentials import get_credentials_manager
from src.app.common_modules.aws.helpers.exceptions import DownloadFailedException
from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.helper_methods.model.dynamodbConfig import DynamodbConfig
from src.resources.version.version import Version


class AwsBoto3:
    def __init__(self):
        self._config = Config(connect_timeout=5, read_timeout=5)
        self._region = 'us-east-2'
        self._credentials_manager = get_credentials_manager()
        self._uses_device_auth = self._credentials_manager.has_device_config()

        # Ensure credentials are available before creating clients (only for device auth)
        if self._uses_device_auth:
            self._ensure_credentials()

        self.s3 = boto3.client('s3', config=self._config, region_name=self._region)
        self.dynamodb = boto3.client('dynamodb', config=self._config, region_name=self._region)
        self.disabled = False
        self.bucket = 'skroot-data'
        self.useCase = Version().getUseCase()
        self.runUid = datetimeToMillis(datetime.datetime.now())

        # Get company ID and S3 prefix from credentials API
        self.customerId = self._credentials_manager.get_company_id()
        s3_prefix = self._credentials_manager.get_s3_prefix()
        if s3_prefix and self.customerId:
            if not s3_prefix.endswith('/'):
                s3_prefix += '/'
            self.runFolder = f'{s3_prefix}{self.useCase}/{self.runUid}'
        else:
            self.runFolder = None

    def _ensure_credentials(self) -> bool:
        """
        Ensure valid AWS credentials are available (device auth only).
        Refreshes credentials if they are expired or expiring soon.

        For legacy AWS credential chain, this is a no-op.

        Returns:
            bool: True if credentials were refreshed and clients need recreation
        """
        if not self._uses_device_auth:
            return False
        return self._credentials_manager.ensure_valid_credentials()

    def _refresh_clients(self):
        """
        Recreate boto3 clients after credential refresh.
        This is needed because boto3 clients cache credentials at creation time.
        """
        self.s3 = boto3.client('s3', config=self._config, region_name=self._region)
        self.dynamodb = boto3.client('dynamodb', config=self._config, region_name=self._region)

    def uploadFile(self, fileLocation, fileType, tags={}) -> bool:
        if not self.disabled and self.runFolder:
            # Ensure credentials are fresh before operation
            if self._ensure_credentials():
                self._refresh_clients()

            try:
                destination = f'{self.runFolder}/{os.path.basename(fileLocation)}'
                self.s3.upload_file(
                    fileLocation, self.bucket, destination,
                    ExtraArgs={'ContentType': fileType,
                               "Tagging": parse.urlencode(tags),
                               "CacheControl": "no-cache"})
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet', extra={"id": "aws"})
                return False
            except:
                logging.exception('Error uploading file to S3.', extra={"id": "aws"})
                return False
            return True
        else:
            return False

    def downloadFile(self, aws_filename, local_filename):
        if not self.disabled:
            # Ensure credentials are fresh before operation
            if self._ensure_credentials():
                self._refresh_clients()

            try:
                self.s3.download_file(self.bucket, aws_filename, local_filename)
            except botocore.exceptions.EndpointConnectionError:
                logging.info('no internet', extra={"id": "aws"})
                self.disabled = True
            except:
                logging.exception("Failed to download release notes")
                raise DownloadFailedException()

    def pushExperimentRow(self, config: DynamodbConfig) -> bool:
        if not self.disabled:
            # Ensure credentials are fresh before operation
            if self._ensure_credentials():
                self._refresh_clients()

            if self.customerId is not None:
                item = {
                    'customerId': {'S': self.customerId},
                    'runUid': {'N': str(self.runUid)},
                    'startDate': {'N': str(config.startDate)},
                    'endDate': {'S': str(config.endDate)},
                    'saturationDate': {'S': str(config.saturationDate)},
                    'lastUpdated': {'N': str(datetimeToMillis(datetime.datetime.now()))},
                    'incubator': {'S': config.incubator},
                    'lotId': {'S': config.lotId},
                    'automatedFlagged': {'BOOL': config.flagged},
                }
                if config.warehouse:
                    item['warehouse'] = {'S': config.warehouse}
                self.dynamodb.put_item(
                    TableName='runs',
                    Item=item
                )
                return True
        return False
