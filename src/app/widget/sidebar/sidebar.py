import csv
import logging
import os
import subprocess
import tkinter as tk
from tkinter import ttk

from src.app.authentication.authentication_popup import AuthenticationPopup
from src.app.authentication.helpers.configuration import AuthConfiguration
from src.app.authentication.helpers.constants import AuthenticationConstants
from src.app.authentication.helpers.exceptions import AuthLogsNotFound, AideLogsNotFound
from src.app.authentication.helpers.functions import getUsers, getAdmins
from src.app.authentication.helpers.logging import extractAuthLogs, extractAideLogs, logAuthAction
from src.app.common_modules.service.software_update import SoftwareUpdate
from src.app.model.menu_item import MenuItem
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.widget.sidebar.manage_users.user_registration import UserRegistration
from src.app.custom_exceptions.common_exceptions import USBDriveNotFoundException
from src.app.helper_methods.helper_functions import getUsbDrive, unmountUSBDrive
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification
from src.app.widget.sidebar.manuals.advanced_setting_document import AdvancedSettingsDocument
from src.app.widget.sidebar.settings.system_configuration_page import SystemConfigurationPage
from src.app.widget.sidebar.manage_users.restore_user_screen import RestoreUserScreen
from src.app.widget.sidebar.manage_users.retire_user_screen import RetireUserScreen
from src.app.widget.sidebar.settings.password_requirements_config import PasswordRequirementsScreen
from src.app.widget.sidebar.manage_users.password_reset_screen import PasswordResetScreen
from src.app.widget.sidebar.manuals.troubleshooting_page import TroubleshootingPage
from src.app.widget.sidebar.manuals.user_guide_page import UserGuidePage


class Sidebar:
    def __init__(self, rootManager: RootManager, bodyFrame, toolbar, softwareUpdate: SoftwareUpdate):
        self.RootManager = rootManager
        self.bodyFrame = bodyFrame
        self.toolbar = toolbar
        self.softwareUpdate = softwareUpdate

        self.menu_open = False
        self.submenu_open = False
        self.active_submenu = None
        self.menu_width = 300
        self.submenu_width = 300

        # Create the menu panel (starts off-screen)
        self.menu_panel = tk.Frame(self.bodyFrame, bg=Colors().primaryColor, width=self.menu_width, pady=10,
                                   highlightbackground=Colors().secondaryColor, borderwidth=2, highlightthickness=2)

        # Create submenu panel (will be positioned when needed)
        self.submenu_panel = tk.Frame(self.bodyFrame, bg=Colors().primaryColor, width=self.submenu_width, pady=10,
                                      highlightbackground=Colors().secondaryColor, borderwidth=2, highlightthickness=2)

        # Create hamburger button (three lines)
        self.menu_button = tk.Button(self.toolbar, text="☰", font=FontTheme().header1, padx=30,
                                     bg=Colors().primaryColor, fg=Colors().secondaryColor, bd=0, highlightthickness=0,
                                     command=self.toggle_menu)

        self.submenus = {
            "Export Data": [
                MenuItem("Export Audit Trail", lambda: exportAuditTrail(self.RootManager)),
                MenuItem("Export Users", lambda: exportUserInfo(self.RootManager)),
            ],
            "Manage Users": [
                MenuItem("Register a User", lambda: registerNewUser(self.RootManager)),
                MenuItem("Reset Password", lambda: resetUserPassword(self.RootManager)),
                MenuItem("Retire User", lambda: retireUser(self.RootManager)),
                MenuItem("Restore User", lambda: restoreRetiredUser(self.RootManager)),
            ],
            "Manuals": [
                MenuItem("User Manual", lambda: UserGuidePage(self.RootManager)),
                MenuItem("Troubleshooting", lambda: TroubleshootingPage(self.RootManager)),
                MenuItem("Advanced Use", lambda: AdvancedSettingsDocument(self.RootManager)),
            ],
            "Settings": [
                MenuItem("Configuration", lambda: systemConfiguration(self.RootManager)),
                MenuItem("Password Rotation", lambda: passwordRequirementsScreen(self.RootManager)),
                MenuItem("System Settings", lambda: systemAdminPage(self.RootManager)),
                MenuItem("Software Update", lambda: updateSoftware(self.softwareUpdate)),
            ],
        }
        self.menu_items = [
            MenuItem("Export Data", lambda: self.show_submenu("Export Data")),
            MenuItem("Manage Users", lambda: self.show_submenu("Manage Users")),
            MenuItem("Manuals", lambda: self.show_submenu("Manuals")),
            MenuItem("Settings", lambda: self.show_submenu("Settings")),
        ]
        self.menu_buttons = {}
        self.create_menu_items()

    def create_menu_items(self):
        """Create menu items in the side panel"""
        style = ttk.Style()

        # Configure the Separator style with a color
        style.configure("Primary.TSeparator", background=Colors().primaryColor)
        menu_title = tk.Label(self.menu_panel, text="Menu", font=FontTheme().header1,
                              bg=Colors().primaryColor, fg=Colors().secondaryColor)
        menu_title.pack(pady=10)
        separator = ttk.Separator(self.menu_panel, orient='horizontal', style="Primary.TSeparator")
        separator.pack(fill=tk.X)

        for item in self.menu_items:
            menu_btn = tk.Button(self.menu_panel, text=item.label, font=FontTheme().primary,
                                 bg=Colors().primaryColor, fg=Colors().secondaryColor, bd=0, anchor="w",
                                 activebackground=Colors().lightPrimaryColor, activeforeground=Colors().secondaryColor,
                                 padx=25, pady=20, width=15, highlightthickness=0,
                                 command=lambda i=item: self.menu_item_clicked(i))
            menu_btn.pack(fill=tk.X)
            self.menu_buttons[item.label] = menu_btn

    def menu_item_clicked(self, item: MenuItem):
        """Handle menu item clicks"""
        if item.label not in self.submenus.keys():
            self.toggle_menu() if self.menu_open else None
        item.invokeFn()

    def show_submenu(self, menu_label):
        """Show the submenu for the selected main menu item"""
        if self.active_submenu == menu_label and self.submenu_open:
            self.hide_submenu()
            return

        # If another submenu is open, hide it first
        if self.submenu_open:
            self.hide_submenu()

        self.active_submenu = menu_label

        for widget in self.submenu_panel.winfo_children():
            widget.destroy()

        # Add title to submenu
        submenu_title = tk.Label(self.submenu_panel, text=menu_label, font=FontTheme().header1,
                                 bg=Colors().primaryColor, fg=Colors().secondaryColor)
        submenu_title.pack(pady=10)

        separator = ttk.Separator(self.submenu_panel, orient='horizontal', style="Primary.TSeparator")
        separator.pack(fill=tk.X)

        # Highlight the active menu button
        for label, btn in self.menu_buttons.items():
            if label == menu_label:
                btn.configure(bg=Colors().lightPrimaryColor)
            else:
                btn.configure(bg=Colors().primaryColor)

        # Add submenu items
        for item in self.submenus.get(menu_label, []):
            submenu_btn = tk.Button(self.submenu_panel, text=item.label, font=FontTheme().primary,
                                    bg=Colors().primaryColor, fg=Colors().secondaryColor, bd=0, anchor="w",
                                    activebackground=Colors().lightPrimaryColor,
                                    activeforeground=Colors().secondaryColor,
                                    padx=25, pady=20, width=15, highlightthickness=0,
                                    command=lambda i=item: self.menu_item_clicked(i))
            submenu_btn.pack(fill=tk.X)

        # Ensure the main menu is open
        if not self.menu_open:
            self.toggle_menu()

        # Calculate position for submenu - right next to main menu
        submenu_x = self.menu_width - 1  # Overlap by 1 pixel for a seamless look

        # Show submenu with a slide animation
        self.submenu_panel.place(x=submenu_x - self.submenu_width, y=0, relheight=1, width=self.submenu_width)
        self.submenu_panel.lift()

        # Animate the submenu sliding in
        for i in range(self.submenu_width + 1):
            if i % 10 == 0:  # Move in increments of 10 for smoother animation
                self.submenu_panel.place(x=submenu_x - self.submenu_width + i, y=0, relheight=1,
                                         width=self.submenu_width)
                self.submenu_panel.update()

        self.submenu_open = True

    def hide_submenu(self):
        """Hide the submenu with animation"""
        if not self.submenu_open:
            return

        # Get current x position
        current_x = self.submenu_panel.winfo_x()

        # Animate closing
        for i in range(self.submenu_width, -1, -10):
            self.submenu_panel.place(x=current_x - (self.submenu_width - i), y=0)
            self.submenu_panel.update()

        self.submenu_panel.place_forget()
        self.submenu_open = False
        self.active_submenu = None

        # Reset all menu button colors
        for btn in self.menu_buttons.values():
            btn.configure(bg=Colors().primaryColor)

    def toggle_menu(self):
        """Toggle the side menu open/closed"""
        if self.menu_open:
            # If submenu is open, close it first
            if self.submenu_open:
                self.hide_submenu()

            # Close menu with animation
            for i in range(self.menu_width, -1, -10):
                self.menu_panel.place(x=-self.menu_width + i, y=0)
                self.menu_panel.update()
            self.menu_open = False
        else:
            # Open menu with animation
            self.menu_panel.lift()
            for i in range(self.menu_width + 1):
                if i % 10 == 0:  # Move in increments of 10 for smoother animation
                    self.menu_panel.place(x=-self.menu_width + i, y=0)
                    self.menu_panel.update()
            self.menu_open = True


def registerNewUser(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager, True)
    if auth.isAuthenticated:
        if AuthConfiguration().authenticationEnabled:
            UserRegistration(rootManager, auth.getUser(), auth.password.get())
        else:
            text_notification.setText("Cannot register a user, authentication is disabled.")


def systemAdminPage(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager, False, True, forceAuthenticate=True)
    if auth.isAuthenticated:
        subprocess.run(["sudo", "chvt", "1"])


def systemConfiguration(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager, False, True, forceAuthenticate=True)
    if auth.isAuthenticated:
        SystemConfigurationPage(rootManager)


def passwordRequirementsScreen(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager, False, True)
    if auth.isAuthenticated:
        if AuthConfiguration().authenticationEnabled:
            PasswordRequirementsScreen(rootManager)
        else:
            text_notification.setText("Cannot reset user passwords, authentication is disabled.")


def resetUserPassword(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager)
    if auth.isAuthenticated:
        if AuthConfiguration().authenticationEnabled:
            PasswordResetScreen(rootManager, auth.getUser())
        else:
            text_notification.setText("Cannot reset user passwords, authentication is disabled.")


def retireUser(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager)
    if auth.isAuthenticated:
        if AuthConfiguration().authenticationEnabled:
            RetireUserScreen(rootManager, auth.getUser())
        else:
            text_notification.setText("Cannot retire a user, authentication is disabled.")


def restoreRetiredUser(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager, True)
    if auth.isAuthenticated:
        if AuthConfiguration().authenticationEnabled:
            RestoreUserScreen(rootManager, auth.getUser())
        else:
            text_notification.setText("Cannot restore a user, authentication is disabled.")


def updateSoftware(softwareUpdater: SoftwareUpdate):
    auth = AuthenticationPopup(softwareUpdater.RootManager)
    if auth.isAuthenticated:
        softwareUpdater.checkForSoftwareUpdates()
        if softwareUpdater.newestZipVersion:
            softwareUpdater.downloadSoftwareUpdate()


def exportUserInfo(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager)
    if auth.isAuthenticated:
        if AuthConfiguration().authenticationEnabled:
            try:
                logAuthAction("User Export", "Initiated", username=auth.getUser())
                driveLocation = getUsbDrive()
                with open(f"{driveLocation}/Users.csv", 'w', newline='') as csvfile:
                    # Define CSV columns
                    fieldnames = ['Username', 'Role', 'Password Last Changed', 'Password Expires', 'Password Inactive', 'Last Active']

                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()

                    for user in getAdmins():
                        logging.info(user.get_dict(), extra={"id": "User Management"})
                        writer.writerow(user.get_dict())

                    for user in getUsers():
                        logging.info(user.get_dict(), extra={"id": "User Management"})
                        writer.writerow(user.get_dict())
                logAuthAction("User Export", "Successful", username=auth.getUser())
                text_notification.setText("User information exported successfully.")
            except:
                logAuthAction("User Export", "Failed", username=auth.getUser())
                text_notification.setText("Failed to export user information.")
                logging.exception("Failed to export user information.")
        else:
            text_notification.setText("Cannot export users, user authentication is disabled.")


def exportAuditTrail(rootManager: RootManager):
    auth = AuthenticationPopup(rootManager)
    if auth.isAuthenticated:
        try:
            driveLocation = getUsbDrive()
            if not os.path.exists(f"{driveLocation}/Audit"):
                os.mkdir(f"{driveLocation}/Audit")
            if not os.path.exists(f"{driveLocation}/Audit/System Logs"):
                os.mkdir(f"{driveLocation}/Audit/System Logs")
            try:
                extractAideLogs(f"{driveLocation}/Audit/System Logs", auth.getUser())
            except AideLogsNotFound:
                text_notification.setText("No file integrity logs found.")
                logging.exception("Failed to extract file integrity logs.", extra={"id": "Audit Trail"})
            extractAuthLogs(
                AuthenticationConstants().loggingGroup,
                f"{driveLocation}/Audit/Auth Trail.csv",
                f"{driveLocation}/Audit/Auth Trail.pdf",
                auth.getUser(),
            )
            text_notification.setText(f"Successfully exported Auth Trail.")
        except USBDriveNotFoundException:
            text_notification.setText(f"USB drive not found. Plug in a USB and try again.")
            logging.exception("USB Drive not found.", extra={"id": "Audit Trail"})
        except AuthLogsNotFound:
            text_notification.setText("Failed to extract authentication logs.")
            logging.exception("Failed to extract authentication logs.", extra={"id": "Audit Trail"})
        except:
            text_notification.setText("Failed to export audit trail.")
            logging.exception("Failed to export audit trail.", extra={"id": "Audit Trail"})
        finally:
            unmountUSBDrive()
