import logging
import os
import shutil
from datetime import datetime

from src.app.authentication.helpers.constants import AuthenticationConstants
from src.app.authentication.helpers.exceptions import AideLogsNotFound, AuthLogsNotFound
from src.app.authentication.helpers.functions import getAdmins, getUsers
from src.app.authentication.helpers.logging import extractAuthLogs, extractAideLogs, logAuthAction
from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.helper_methods.pdf_helpers import createPdf
from src.app.widget import text_notification


def createAuditTrail(user: str, driveLocation: str, startDate: datetime.date, endDate: datetime.date):
    try:
        logAuthAction("Audit Trail Export", "Initiated", username=user)
        createAuthLogs(driveLocation, user, startDate, endDate)
        createAideLogs(driveLocation, user)
        text_notification.setText(f"Successfully exported Auth Trail.")
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
        text_notification.setText("User information exported successfully.")
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
        text_notification.setText("Error extracting file integrity logs.")
        logging.exception("Failed to extract file integrity logs.", extra={"id": "Audit Trail"})


def zipTempDir(tempDir, outputZipFile):
    shutil.make_archive(outputZipFile.replace('.zip', ''), 'zip', tempDir)

