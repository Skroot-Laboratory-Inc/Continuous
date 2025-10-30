from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.model.menu_item import MenuItem
from src.app.widget.sidebar.menus.base_menu import BaseMenu


class TertiaryMenu(BaseMenu):
    """Tertiary menu panel for sub-submenu options"""

    def __init__(self, parent_frame, width, rootManager, sessionManager: SessionManager, onActionExecuted=None):
        super().__init__(parent_frame, width, rootManager, sessionManager, onActionExecuted)
        self.activeMenu = None

        self.menus = {
            "Modify User": [
                MenuItem("Reset Password", lambda: self.resetUserPassword()),
                MenuItem("Retire User", lambda: self.retireUser()),
                MenuItem("Edit User Role", lambda: self.modifyGroup()),
            ],
            "Manage Passwords": [
                MenuItem("Password\nConfiguration", lambda: self.passwordConfigurationsScreen()),
                MenuItem("Password\nRequirements", lambda: self.passwordRequirementsScreen()),
            ],
            "Configuration": [
                MenuItem("System Configuration", lambda: self.systemConfiguration()),
                MenuItem("Pump Configuration", lambda: self.pumpConfiguration()),
                MenuItem("Secondary Axis", lambda: self.setSecondaryAxis()),
                MenuItem("System Time", lambda: self.setSystemTime()),
            ]
        }

    def showMenu(self, menuLabel, mainMenuWidth, submenuWidth):
        """Show the tertiary menu for the selected submenu item"""
        if self.activeMenu == menuLabel and self.isOpen:
            self.hideMenu()
            return

        # If another tertiary menu is open, hide it first
        if self.isOpen:
            self.hideMenu()

        self.activeMenu = menuLabel
        self.clearButtons()
        self.destroyChildren()

        self.createTitle(menuLabel)
        menu_items = self.menus.get(menuLabel, [])
        self.createButtons(menu_items)

        # Calculate position and animate in
        final_x = mainMenuWidth + submenuWidth
        self.slideIn(final_x)
        self.isOpen = True

    def hideMenu(self):
        """Hide the tertiary menu with animation"""
        if not self.isOpen:
            return

        current_x = self.panel.winfo_x()
        end_x = current_x + self.width
        self.slideOut(current_x, end_x)

        self.clearButtons()
        self.isOpen = False
        self.activeMenu = None

    def menuItemClicked(self, item):
        """Handle tertiary menu item clicks"""
        # Execute the function and close the sidebar
        if self.onActionExecuted:
            self.onActionExecuted()
        item.invokeFn()

    def setActiveItem(self, item_label):
        """Highlight the active tertiary menu item"""
        self.highlightButton(item_label)
