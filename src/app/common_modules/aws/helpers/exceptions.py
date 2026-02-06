import logging

from botocore.exceptions import ClientError

EXPIRED_TOKEN_CODES = {'ExpiredToken', 'ExpiredTokenException', 'RequestExpired'}


class AwsException(Exception):
    """ Base class for the aws related exceptions. """


class DownloadFailedException(AwsException):
    """ Base class for the aws related exceptions. """


class ExpiredTokenException(AwsException):
    """ Raised when AWS credentials have expired. """


def raise_on_expired_token(error: ClientError):
    """Check if a ClientError is due to an expired token and raise ExpiredTokenException if so."""
    error_code = error.response['Error']['Code']
    if error_code in EXPIRED_TOKEN_CODES:
        logging.info("AWS token is expired.", extra={"id": "aws"})
        raise ExpiredTokenException(str(error)) from error

