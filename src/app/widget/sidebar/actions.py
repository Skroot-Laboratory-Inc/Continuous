import glob
import logging
import tempfile
from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.app.authentication.helpers.configuration import AuthConfiguration
from src.app.authentication.helpers.decorators import requireAdmin, requireSystemAdmin, requireUser, \
    forceRequireSystemAdmin
from src.app.authentication.helpers.logging import logAuthAction
from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.common_modules.service.software_update import SoftwareUpdate
from src.app.custom_exceptions.common_exceptions import USBDriveNotFoundException, UserConfirmationException
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.helper_methods.helper_functions import getUsbDrive, unmountUSBDrive
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification
from src.app.widget.sidebar.helpers.functions import createAuditTrail, createUserInfoPdf, zipTempDir, copyRunFile
from src.app.widget.sidebar.helpers.run_exporter import RunExporter
from src.app.widget.sidebar.manage_users.modify_user_group import ModifyUserGroup
from src.app.widget.sidebar.manage_users.password_reset_screen import PasswordResetScreen
from src.app.widget.sidebar.manage_users.restore_user_screen import RestoreUserScreen
from src.app.widget.sidebar.manage_users.retire_user_screen import RetireUserScreen
from src.app.widget.sidebar.manage_users.user_registration import UserRegistration
from src.app.widget.sidebar.settings.date_range_picker import DateRangePicker
from src.app.widget.sidebar.settings.password_requirements import PasswordRequirementsScreen
from src.app.widget.sidebar.settings.password_rotation import PasswordRotationScreen
from src.app.widget.sidebar.settings.pump_configuration_page import PumpConfigurationPage
from src.app.widget.sidebar.settings.system_configuration_page import SystemConfigurationPage
from src.app.widget.sidebar.settings.system_time_manager import SystemTimeManager


class SideBarActions:
    def __init__(self, rootManager: RootManager, sessionManager: SessionManager):
        self.rootManager = rootManager
        self.sessionManager = sessionManager

    @forceRequireSystemAdmin
    def systemConfiguration(self):
        SystemConfigurationPage(self.rootManager, self.sessionManager.getUser())

    @requireUser
    def pumpConfiguration(self):
        PumpConfigurationPage(self.rootManager, self.sessionManager.getUser())

    @requireSystemAdmin
    def passwordRequirementsScreen(self):
        if AuthConfiguration().getConfig():
            PasswordRequirementsScreen(self.rootManager, self.sessionManager.getUser())
        else:
            text_notification.setText("Cannot change password requirements, authentication is disabled.")

    @requireSystemAdmin
    def passwordConfigurationsScreen(self):
        if AuthConfiguration().getConfig():
            PasswordRotationScreen(self.rootManager, self.sessionManager.getUser())
        else:
            text_notification.setText("Cannot change password configurations, authentication is disabled.")

    @requireUser
    def setSystemTime(self):
        SystemTimeManager(self.rootManager, self.sessionManager.getUser())

    @requireAdmin
    def registerNewUser(self):
        if AuthConfiguration().getConfig():
            UserRegistration(self.rootManager, self.sessionManager.getUser())
        else:
            text_notification.setText("Cannot register a user, authentication is disabled.")

    @requireAdmin
    def modifyGroup(self):
        if AuthConfiguration().getConfig():
            ModifyUserGroup(self.rootManager, self.sessionManager.getUser())
        else:
            text_notification.setText("Cannot modify a user's role, authentication is disabled.")

    @requireAdmin
    def restoreRetiredUser(self):
        if AuthConfiguration().getConfig():
            RestoreUserScreen(self.rootManager, self.sessionManager.getUser())
        else:
            text_notification.setText("Cannot restore a user, authentication is disabled.")

    @requireUser
    def resetUserPassword(self):
        if AuthConfiguration().getConfig():
            PasswordResetScreen(self.rootManager, self.sessionManager.getUser())
        else:
            text_notification.setText("Cannot reset user passwords, authentication is disabled.")

    @requireUser
    def retireUser(self):
        if AuthConfiguration().getConfig():
            RetireUserScreen(self.rootManager, self.sessionManager.getUser())
        else:
            text_notification.setText("Cannot retire a user, authentication is disabled.")

    @requireUser
    def exportUserInfo(self):
        if AuthConfiguration().getConfig():
            try:
                driveLocation = getUsbDrive()
                createUserInfoPdf(self.sessionManager.getUser(), driveLocation)
            except USBDriveNotFoundException:
                text_notification.setText(f"USB drive not found. \nPlease plug in USB drive and try again.")
                logging.exception("USB Drive not found.", extra={"id": "User Management"})
            finally:
                unmountUSBDrive()
        else:
            text_notification.setText("Cannot export users, user authentication is disabled.")

    @requireUser
    def exportAuditTrail(self):
        try:
            username = self.sessionManager.getUser()
            dateRangePicker = DateRangePicker(self.rootManager)
            driveLocation = getUsbDrive()
            createAuditTrail(username, driveLocation, dateRangePicker.startDate, dateRangePicker.endDate)
        except USBDriveNotFoundException:
            text_notification.setText(f"USB drive not found. \nPlease plug in USB drive and try again.")
            logging.exception("USB Drive not found.", extra={"id": "Audit Trail"})
        except UserConfirmationException:
            text_notification.setText("Audit trail export cancelled.")
            logging.exception("Authentication Log Export Cancelled by user.", extra={"id": "Audit Trail"})
        finally:
            unmountUSBDrive()

    @requireUser
    def exportRun(self):
        if AuthConfiguration().getConfig():
            RunExporter(self.rootManager, self.sessionManager.getUser())
        else:
            RunExporter(self.rootManager)

    @requireUser
    def exportAll(self):
        username = self.sessionManager.getUser()
        try:
            driveLocation = getUsbDrive()
            with tempfile.TemporaryDirectory() as outputDir:
                logAuthAction("Export All", "Initiated", username)
                createUserInfoPdf(username, outputDir)
                createAuditTrail(username, outputDir, datetime.today().date() - relativedelta(years=1), datetime.today().date())
                runDirectories = glob.glob(f"{CommonFileManager().getDataSavePath()}/*")
                for directory in runDirectories:
                    runId = directory.split("/")[-1].split("_")[-1]
                    copyRunFile(username, outputDir, runId)
                zipTempDir(
                    outputDir,
                    f"{driveLocation}/System Snapshot_{datetimeToMillis(datetime.now())}.zip",
                )
            logAuthAction("Export All", "Successful", username)
            text_notification.setText("System information exported to USB drive.")
        except USBDriveNotFoundException:
            text_notification.setText(f"USB drive not found. \nPlease plug in USB drive and try again.")
            logging.exception("USB Drive not found.", extra={"id": "Audit Trail"})
        except:
            logAuthAction("Export All", "Failed", username)
            text_notification.setText(f"Failed to export audit trail.")
            logging.exception("Failed to export data.", extra={"id": "Audit Trail"})
        finally:
            unmountUSBDrive()

    @requireUser
    def updateSoftware(self, softwareUpdater: SoftwareUpdate):
        softwareUpdater.checkForSoftwareUpdates()
        if softwareUpdater.newestZipVersion:
            softwareUpdater.downloadSoftwareUpdate()
