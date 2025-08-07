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

        self.menuWidth = 350
        self.submenuWidth = 350
        self.tertiary_menu_width = 350

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

        # Set up click-outside-to-close functionality
        self.setupClickOutsideToClose()

    def setupClickOutsideToClose(self):
        """Set up event bindings for click-outside-to-close functionality"""
        root = self.rootManager.getRoot()
        root.bind("<Button-1>", self.handleRootClick, add="+")

    def handleRootClick(self, event):
        """Handle clicks anywhere in the application"""
        if not (self.mainMenu.isOpen or self.subMenu.isOpen or self.tertiaryMenu.isOpen):
            return
        if self.isClickInsideMenus(event.widget):
            return
        # Click was outside menus, so close them
        self.closeAllMenus()

    def isClickInsideMenus(self, widget):
        """Check if the clicked widget is inside any of the menu panels or hamburger button"""
        # Check if click was on hamburger button
        if widget == self.mainMenu.hamburgerButton:
            return True

        menu_panels = [
            self.mainMenu.panel,
            self.subMenu.panel,
            self.tertiaryMenu.panel
        ]

        for panel in menu_panels:
            if self.isWidgetInside(widget, panel):
                return True

        return False

    def isWidgetInside(self, widget, container):
        """Recursively check if a widget is inside a container"""
        if widget == container:
            return True

        parent = widget.master if hasattr(widget, 'master') else None
        if parent is None:
            return False

        return self.isWidgetInside(parent, container)

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
