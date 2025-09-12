import glob
import logging
import os
import shutil
import subprocess
from datetime import datetime

import boto3
from botocore.exceptions import NoCredentialsError, ClientError, BotoCoreError

from src.app.authentication.helpers.constants import AuthenticationConstants
from src.app.authentication.helpers.exceptions import AideLogsNotFound, AuthLogsNotFound
from src.app.authentication.helpers.functions import getAdmins, getUsers
from src.app.authentication.helpers.logging import extractAuthLogs, extractAideLogs, logAuthAction
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.helper_methods.pdf_helpers import createPdf
from src.app.widget import text_notification


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


def isAwsConnected():
    """
    Check if the device is connected to AWS by calling STS get-caller-identity.

    Returns:
        bool: True if connected to AWS, False otherwise
    """
    try:
        sts_client = boto3.client('sts')
        response = sts_client.get_caller_identity()
        logging.info(f"Currently logged in as {response.get('Arn')}", extra={"id": "AWS"})
        return True
    except NoCredentialsError:
        # No AWS credentials configured
        return False
    except ClientError:
        # AWS service error (e.g., invalid credentials, network issues)
        return False
    except BotoCoreError:
        # Other boto3/botocore errors
        return False
    except Exception:
        # Any other unexpected error
        return False
