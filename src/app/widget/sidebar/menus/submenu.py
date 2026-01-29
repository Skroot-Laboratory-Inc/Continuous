import logging
from typing import List

from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.helper_methods.model.menu_item import MenuItem
from src.app.widget.sidebar.helpers.functions import hasValidAwsCredentials, validateAwsCredentialsSync
from src.app.widget.sidebar.manuals.advanced_setting_document import AdvancedSettingsDocument
from src.app.widget.sidebar.manuals.troubleshooting_page import TroubleshootingPage
from src.app.widget.sidebar.manuals.user_guide_page import UserGuidePage
from src.app.widget.sidebar.menus.base_menu import BaseMenu


class SubMenu(BaseMenu):
    """Submenu panel that displays based on main menu selection"""

    def __init__(self, parent_frame, width, rootManager, sessionManager: SessionManager, requestMenu=None,
                 onActionExecuted=None, softwareUpdate=None, connectivityButton=None):
        super().__init__(parent_frame, width, rootManager, sessionManager, onActionExecuted)
        self.requestMenu = requestMenu
        self.softwareUpdate = softwareUpdate
        self.connectivityButton = connectivityButton
        self.active_menu = None
        hasValidAwsCredentials()  # Pre-check AWS credentials on init

        self.submenus = {
            "Export Data": [
                MenuItem("Export Run", lambda: self.exportRun()),
                MenuItem("Export Audit Trail", lambda: self.exportAuditTrail()),
                MenuItem("Export Users", lambda: self.exportUserInfo()),
                MenuItem("Export All", lambda: self.exportAll()),
            ],
            "Manage Users": [
                MenuItem("Register User", lambda: self.registerNewUser()),
                MenuItem("Modify User", lambda: self.requestMenu("Modify User")),
                MenuItem("Restore User", lambda: self.restoreRetiredUser()),
            ],
            "Manuals": [
                MenuItem("User Manual", lambda: UserGuidePage(self.rootManager)),
                MenuItem("Troubleshooting", lambda: TroubleshootingPage(self.rootManager)),
                MenuItem("Advanced Use", lambda: AdvancedSettingsDocument(self.rootManager)),
            ],
            "Settings": []  # Dynamically built in _getSettingsMenu()
        }

    def _getSettingsMenu(self) -> List[MenuItem]:
        """Build Settings menu dynamically based on current connectivity status"""
        settingsMenu: List[MenuItem] = [
            MenuItem("Configuration", lambda: self.requestMenu("Configuration")),
            MenuItem("Manage Passwords", lambda: self.requestMenu("Manage Passwords")),
        ]
        hasCredentials = hasValidAwsCredentials()
        hasInternet = self.connectivityButton.isConnected if self.connectivityButton else False
        logging.info(f"AWS credentials valid: {hasCredentials}, Has Internet: {hasInternet}", extra={"id": "AWS"})
        if hasCredentials and hasInternet:
            settingsMenu.append(MenuItem("Software Update", lambda: self.updateSoftware(self.softwareUpdate)))
        return settingsMenu

    def showMenu(self, menu_label, main_menu_width):
        """Show the submenu for the selected main menu item"""
        if self.active_menu == menu_label and self.isOpen:
            self.hideMenu()
            return

        # If another submenu is open, hide it first
        if self.isOpen:
            self.hideMenu()

        self.active_menu = menu_label
        self.clearButtons()
        self.destroyChildren()

        self.createTitle(menu_label)
        if menu_label == "Settings":
            menu_items = self._getSettingsMenu()
        else:
            menu_items = self.submenus.get(menu_label, [])

        self.createButtons(menu_items)

        # Calculate position and animate in
        final_x = main_menu_width
        self.slideIn(final_x)
        self.isOpen = True

    def hideMenu(self):
        """Hide the submenu with animation"""
        if not self.isOpen:
            return

        current_x = self.panel.winfo_x()
        end_x = current_x + self.width
        self.slideOut(current_x, end_x)

        self.clearButtons()
        self.isOpen = False
        self.active_menu = None

    def requestMenu(self, menu_label):
        """Request the tertiary menu to be shown"""
        if self.requestMenu:
            self.requestMenu(menu_label)

    def menuItemClicked(self, item):
        """Handle submenu item clicks"""
        if item.label in ["Modify User", "Manage Passwords", "Configuration"]:  # Items with tertiary menus
            # Don't close sidebar, just execute the function
            item.invokeFn()
        else:
            if self.onActionExecuted:
                self.onActionExecuted()
            item.invokeFn()

    def setActiveItem(self, item_label):
        """Highlight the active submenu item"""
        self.highlightButton(item_label)
