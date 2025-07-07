import tkinter as tk

from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.model.menu_item import MenuItem
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.widget.sidebar.menus.base_menu import BaseMenu


class MainMenu(BaseMenu):
    """Main menu panel with hamburger button and primary menu items"""

    def __init__(self, parent_frame, toolbar, width, rootManager, sessionManager: SessionManager, onMenuClick=None, onMenuToggle=None,
                 onActionExecuted=None):
        super().__init__(parent_frame, width, rootManager, sessionManager, onActionExecuted)
        self.toolbar = toolbar
        self.onMenuClick = onMenuClick
        self.onMenuToggle = onMenuToggle

        self.hamburgerButton = tk.Button(
            self.toolbar,
            text="☰",
            font=FontTheme().header1,
            padx=30,
            bg=Colors().primaryColor,
            fg=Colors().secondaryColor,
            bd=0,
            highlightthickness=0,
            command=self.toggleMenu
        )

        self.items = [
            MenuItem("Export Data", lambda: self.handleMenuClick("Export Data")),
            MenuItem("Manage Users", lambda: self.handleMenuClick("Manage Users")),
            # MenuItem("Manuals", lambda: self.handleMenuClick("Manuals")),
            MenuItem("Settings", lambda: self.handleMenuClick("Settings")),
        ]

        self.createItems()

    def createItems(self):
        """Create the main menu items"""
        self.createTitle("Menu")
        self.createButtons(self.items)

    def handleMenuClick(self, menu_label):
        """Handle menu item clicks and notify parent"""
        if self.onMenuClick:
            self.onMenuClick(menu_label)

    def toggleMenu(self):
        """Toggle the main menu (delegate to parent sidebar)"""
        if self.onMenuToggle:
            self.onMenuToggle()

    def openMenu(self):
        """Open the main menu with animation"""
        if not self.isOpen:
            self.slideIn(0)
            self.isOpen = True

    def closeMenu(self):
        """Close the main menu with animation"""
        if self.isOpen:
            self.slideOut(0, -self.width)
            self.isOpen = False
            self.resetButtonColors()

    def menuItemClicked(self, item):
        """Handle main menu item clicks - don't close sidebar for navigation items"""
        item.invokeFn()

    def setActiveItem(self, item_label):
        """Highlight the active menu item"""
        self.highlightButton(item_label)
