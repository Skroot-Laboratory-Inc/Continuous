import glob
import logging
import os
import shutil
import subprocess
from datetime import datetime

import boto3
from botocore.exceptions import NoCredentialsError, ClientError, BotoCoreError

from src.app.common_modules.authentication.helpers.constants import AuthenticationConstants
from src.app.common_modules.authentication.helpers.exceptions import AuthLogsNotFound, AideLogsNotFound
from src.app.common_modules.authentication.helpers.functions import getAdmins, getUsers
from src.app.common_modules.authentication.helpers.logging import extractAuthLogs, extractAideLogs, logAuthAction
from src.app.common_modules.aws.device_credentials import get_credentials_manager
from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.helper_methods.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.pdf_helpers import createPdf
from src.app.widget import text_notification

# Cache for AWS credentials validation (checked once, cached forever)
_aws_credentials_validated = None


def createAuditTrail(user: str, driveLocation: str, startDate: datetime.date, endDate: datetime.date):
    try:
        logAuthAction("Audit Trail Export", "Initiated", username=user)
        createAuthLogs(driveLocation, user, startDate, endDate)
        createAideLogs(driveLocation, user)
        text_notification.setText("Audit trail exported to USB drive.")
    except AuthLogsNotFound:
        logAuthAction("Audit Trail Export", "Failed", username=user)
        text_notification.setText("Failed to extract authentication logs.")
        logging.exception("Failed to extract authentication logs.", extra={"id": "Audit Trail"})
    except:
        logAuthAction("Audit Trail Export", "Failed", username=user)
        text_notification.setText("Failed to export audit trail.")
        logging.exception("Failed to export audit trail.", extra={"id": "Audit Trail"})


def createUserInfoPdf(username: str, driveLocation: str):
    try:
        if not os.path.exists(f"{driveLocation}/Audit Trail"):
            os.mkdir(f"{driveLocation}/Audit Trail")
        logAuthAction("User Export", "Initiated", username=username)
        fieldnames = [
            'Username', 'Role', 'Password Last Changed', 'Password Expires', 'Password Inactive', 'Last Active',
        ]
        data = [fieldnames]

        for admin in getAdmins():
            row = [admin.get_dict().get(field, '-') for field in fieldnames]
            data.append(row)

        for user in getUsers():
            row = [user.get_dict().get(field, '-') for field in fieldnames]
            data.append(row)

        createPdf(
            data,
            f"{driveLocation}/Audit Trail/Users_{datetimeToMillis(datetime.now())}.pdf",
            "User Account Details",
            username,
        )
        logAuthAction("User Export", "Successful", username=username)
        text_notification.setText("User information exported to USB drive.")
    except:
        logAuthAction("User Export", "Failed", username=username)
        text_notification.setText("Failed to export user information.")
        logging.exception("Failed to export user information.")


def createAuthLogs(driveLocation: str, user: str, startDate: datetime.date, endDate: datetime.date):
    if not os.path.exists(f"{driveLocation}/Audit Trail"):
        os.mkdir(f"{driveLocation}/Audit Trail")
    extractAuthLogs(
        AuthenticationConstants().loggingGroup,
        f"{driveLocation}/Audit Trail/Audit Trail_{datetimeToMillis(datetime.now())}.pdf",
        user,
        startDate,
        endDate,
    )


def createAideLogs(driveLocation: str, user: str):
    if not os.path.exists(f"{driveLocation}/Audit Trail"):
        os.mkdir(f"{driveLocation}/Audit Trail")
    if not os.path.exists(f"{driveLocation}/Audit Trail/System Logs"):
        os.mkdir(f"{driveLocation}/Audit Trail/System Logs")
    try:
        extractAideLogs(f"{driveLocation}/Audit Trail/System Logs", user)
    except AideLogsNotFound:
        text_notification.setText("Failed to extract file integrity logs.")
        logging.exception("Failed to extract file integrity logs.", extra={"id": "Audit Trail"})


def zipTempDir(tempDir, outputZipFile):
    shutil.make_archive(outputZipFile.replace('.zip', ''), 'zip', tempDir)


def copyRunFile(user: str, driveLocation: str, runId: str):
    if not os.path.exists(f"{driveLocation}/Run Results"):
        os.mkdir(f"{driveLocation}/Run Results")
    runFiles = glob.glob(f"{CommonFileManager().getDataSavePath()}/*_{runId}/smoothAnalyzed.csv")
    for file in runFiles:
        shutil.copyfile(
            file,
            f"{driveLocation}/Run Results/{os.path.basename(os.path.dirname(file))}.csv",
        )


def setHostname(hostname: str):
    try:
        subprocess.run(['sudo', 'hostnamectl', 'set-hostname', hostname],
                       check=True, capture_output=True, text=True)
        subprocess.run(["sudo", "sed" "-i", '"s/127.0.1.1.*/127.0.1.1', f"{hostname}/", "/etc/hosts"],
                       check=True, capture_output=True, text=True)

        text_notification.setText(f"Device ID updated to {hostname}.")
        return True
    except subprocess.CalledProcessError as e:
        text_notification.setText("Failed to update Device ID.")
        logging.exception("Failed to update machine hostname", extra={"id": "Hostname"})
        return False


def hasValidAwsCredentials():
    """
    Check if valid AWS credentials are available.

    Uses device-based authentication if device config exists, otherwise falls back
    to legacy AWS credential chain (environment variables, ~/.aws/credentials, etc.).

    This function returns immediately using cached state if available.
    If credentials haven't been validated yet, it triggers background validation
    and returns False (conservative default).

    For UI responsiveness, this function never blocks on network calls.
    Use validateAwsCredentialsSync() for synchronous validation when needed.

    Returns:
        bool: True if AWS credentials are known to be valid, False otherwise
    """
    credentials_manager = get_credentials_manager()

    # Return cached validation state if available
    cached_state = credentials_manager.get_cached_validation_state()
    if cached_state is not None:
        # If using device auth and we have cached credentials that are still valid, return cached state
        if credentials_manager.has_device_config() and credentials_manager.has_valid_cached_credentials():
            return cached_state
        # For legacy auth or expiring device credentials, trigger background refresh
        if credentials_manager.has_device_config():
            credentials_manager.ensure_valid_credentials_async()
        return cached_state

    # No cached state yet - trigger background validation and return False
    # This ensures the UI doesn't block on first load
    _triggerBackgroundValidation()
    return False


def _triggerBackgroundValidation():
    """
    Trigger AWS credential validation in a background thread.
    Updates the cached validation state when complete.
    """
    import threading

    def _validate():
        validateAwsCredentialsSync()

    thread = threading.Thread(target=_validate, daemon=True)
    thread.start()


def validateAwsCredentialsSync() -> bool:
    """
    Synchronously validate AWS credentials.

    Uses device-based authentication if device config exists (/etc/skroot/device.json
    on Linux or %PROGRAMDATA%\\Skroot\\device.json on Windows), otherwise falls back
    to the legacy AWS credential chain (environment variables, ~/.aws/credentials, etc.).

    This function WILL block on network calls. Use hasValidAwsCredentials()
    for non-blocking checks in UI code.

    Returns:
        bool: True if AWS credentials are valid, False otherwise
    """
    global _aws_credentials_validated

    credentials_manager = get_credentials_manager()

    # Check if device config exists - use device auth if available
    if credentials_manager.has_device_config():
        logging.info("Using device-based AWS authentication", extra={"id": "AWS"})
        # Ensure we have valid credentials (fetches/refreshes as needed)
        if not credentials_manager.ensure_valid_credentials():
            logging.warning("Failed to obtain AWS credentials from device authentication", extra={"id": "AWS"})
            _aws_credentials_validated = False
            credentials_manager.set_validation_state(False)
            return False
    else:
        # Fall back to legacy AWS credential chain
        logging.info("Device config not found - using legacy AWS credential chain", extra={"id": "AWS"})

    # Validate credentials with STS (works for both device and legacy auth)
    try:
        sts_client = boto3.client('sts', region_name='us-east-2')
        response = sts_client.get_caller_identity()
        caller_arn = response.get('Arn')
        logging.info(f"Currently logged in as {caller_arn}", extra={"id": "AWS"})
        _aws_credentials_validated = True
        credentials_manager.set_validation_state(True, caller_arn)
    except NoCredentialsError:
        logging.error("No AWS credentials available", extra={"id": "AWS"})
        _aws_credentials_validated = False
        credentials_manager.set_validation_state(False)
    except ClientError as e:
        logging.error(f"AWS credentials validation failed: {e}", extra={"id": "AWS"})
        _aws_credentials_validated = False
        credentials_manager.set_validation_state(False)
    except BotoCoreError as e:
        logging.error(f"AWS credentials validation error: {e}", extra={"id": "AWS"})
        _aws_credentials_validated = False
        credentials_manager.set_validation_state(False)
    except Exception as e:
        logging.error(f"Unexpected error validating AWS credentials: {e}", extra={"id": "AWS"})
        _aws_credentials_validated = False
        credentials_manager.set_validation_state(False)

    logging.info(f"AWS credentials valid: {_aws_credentials_validated}", extra={"id": "AWS"})
    return _aws_credentials_validated


def getAwsCallerArn() -> str:
    """
    Get the ARN of the currently authenticated AWS caller.

    Returns:
        str: The ARN string, or empty string if not available
    """
    credentials_manager = get_credentials_manager()
    arn = credentials_manager.get_caller_arn()
    return arn if arn else ""


def isAwsConnected():
    """
    Deprecated: Use hasValidAwsCredentials() instead for credential checks,
    and combine with internet connectivity check from ConnectivityButton.

    This function is kept for backward compatibility.
    """
    return hasValidAwsCredentials()
