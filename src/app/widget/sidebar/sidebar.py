from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.common_modules.service.software_update import SoftwareUpdate
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.sidebar.menus.main_menu import MainMenu
from src.app.widget.sidebar.menus.submenu import SubMenu
from src.app.widget.sidebar.menus.tertiary_menu import TertiaryMenu


class Sidebar:
    """Main sidebar controller that manages all menu levels"""

    def __init__(self, rootManager: RootManager, sessionManager: SessionManager, bodyFrame, toolbar, softwareUpdate: SoftwareUpdate):
        self.rootManager = rootManager
        self.softwareUpdate = softwareUpdate
        self.SessionManager = sessionManager
        self.bodyFrame = bodyFrame
        self.toolbar = toolbar

        self.menuWidth = 266
        self.submenuWidth = 266
        self.tertiary_menu_width = 266

        self.mainMenu = MainMenu(
            parent_frame=self.bodyFrame,
            toolbar=self.toolbar,
            width=self.menuWidth,
            rootManager=self.rootManager,
            sessionManager=self.SessionManager,
            onMenuClick=self.handleMainMenuClick,
            onMenuToggle=self.toggleMenu,
            onActionExecuted=self.closeAllMenus
        )

        self.subMenu = SubMenu(
            parent_frame=self.bodyFrame,
            width=self.submenuWidth,
            rootManager=self.rootManager,
            sessionManager=self.SessionManager,
            requestMenu=self.handleTertiaryMenuClick,
            onActionExecuted=self.closeAllMenus,
            softwareUpdate=self.softwareUpdate
        )

        self.tertiaryMenu = TertiaryMenu(
            parent_frame=self.bodyFrame,
            width=self.tertiary_menu_width,
            rootManager=self.rootManager,
            sessionManager=self.SessionManager,
            onActionExecuted=self.closeAllMenus
        )

    def handleMainMenuClick(self, menu_label):
        """Handle clicks from the main menu"""
        if self.tertiaryMenu.isOpen:
            self.tertiaryMenu.hideMenu()

        self.subMenu.showMenu(menu_label, self.menuWidth)
        self.mainMenu.setActiveItem(menu_label)

    def handleTertiaryMenuClick(self, menu_label):
        """Handle requests to show tertiary menu"""
        self.tertiaryMenu.showMenu(
            menu_label,
            self.menuWidth,
            self.submenuWidth
        )

        self.subMenu.setActiveItem(menu_label)

    def toggleMenu(self):
        """Toggle the main menu (called by hamburger button)"""
        if self.mainMenu.isOpen:
            if self.tertiaryMenu.isOpen:
                self.tertiaryMenu.hideMenu()
            if self.subMenu.isOpen:
                self.subMenu.hideMenu()
            self.mainMenu.closeMenu()
        else:
            self.mainMenu.openMenu()

    def closeAllMenus(self):
        """Close all menus when an action is executed"""
        if self.tertiaryMenu.isOpen:
            self.tertiaryMenu.hideMenu()
        if self.subMenu.isOpen:
            self.subMenu.hideMenu()
        if self.mainMenu.isOpen:
            self.mainMenu.closeMenu()

    @property
    def getHamburger(self):
        """Expose the hamburger button for external access"""
        return self.mainMenu.hamburgerButton
