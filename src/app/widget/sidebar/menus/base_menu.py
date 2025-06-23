import tkinter as tk
from tkinter import ttk

from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.widget.sidebar.actions import SideBarActions


class BaseMenu(SideBarActions):
    """Base class for all menu panels with grid-based even spacing"""

    def __init__(self, parent_frame, width, rootManager, sessionManager: SessionManager, onActionExecuted=None):
        super().__init__(rootManager, sessionManager)
        self.parent_frame = parent_frame
        self.width = width
        self.rootManager = rootManager
        self.onActionExecuted = onActionExecuted
        self.isOpen = False
        self.buttons = {}

        # Create the menu panel
        self.panel = tk.Frame(
            self.parent_frame,
            bg=Colors().primaryColor,
            width=self.width,
            pady=10,
            highlightbackground=Colors().secondaryColor,
            borderwidth=2,
            highlightthickness=2
        )
        self.panel.pack_propagate(False)
        self.panel.grid_propagate(False)

        # Configure grid weights for even distribution
        self.panel.grid_columnconfigure(0, weight=1)

    def createTitle(self, title_text):
        """Create a title label for the menu"""
        title = tk.Label(
            self.panel,
            text=title_text,
            font=FontTheme().header1,
            bg=Colors().primaryColor,
            fg=Colors().secondaryColor
        )
        title.grid(row=0, column=0, pady=10, sticky="ew")

        separator = ttk.Separator(self.panel, orient='horizontal', style="Primary.TSeparator")
        separator.grid(row=1, column=0, sticky="ew", padx=10)
        return title

    def createButtons(self, items):
        """Create buttons using grid layout for even distribution"""
        # Title and separator take rows 0 and 1
        start_row = 2

        for i, item in enumerate(items):
            row = start_row + i
            self.panel.grid_rowconfigure(row, weight=1)

            btn = tk.Button(
                self.panel,
                text=item.label,
                font=FontTheme().primary,
                bg=Colors().primaryColor,
                fg=Colors().secondaryColor,
                bd=0,
                anchor="center",
                activebackground=Colors().lightPrimaryColor,
                activeforeground=Colors().secondaryColor,
                padx=15,
                highlightthickness=0,
                command=lambda i=item: self.menuItemClicked(i)
            )
            btn.grid(row=row, column=0, sticky="nsew")
            self.buttons[item.label] = btn

    def highlightButton(self, activeButton):
        """Highlight the active button and reset others"""
        for label, btn in self.buttons.items():
            if label == activeButton:
                btn.configure(bg=Colors().lightPrimaryColor)
            else:
                btn.configure(bg=Colors().primaryColor)

    def resetButtonColors(self):
        """Reset all button colors to default"""
        for btn in self.buttons.values():
            btn.configure(bg=Colors().primaryColor)

    def clearButtons(self):
        """Clear the buttons dictionary"""
        self.buttons.clear()

    def destroyChildren(self):
        """Destroy all child widgets and reset grid configuration"""
        for widget in self.panel.winfo_children():
            widget.destroy()

        for i in range(20):  # Clear potential row configurations
            self.panel.grid_rowconfigure(i, weight=0)

    def slideIn(self, start_x, end_x):
        """Animate the panel sliding in from start_x to end_x"""
        self.panel.place(x=start_x, y=0, relheight=1, width=self.width)
        self.panel.lift()

        for i in range(0, abs(end_x - start_x) + 1, 10):
            if start_x < end_x:  # Sliding right
                current_x = start_x + i
            else:  # Sliding left
                current_x = start_x - i

            self.panel.place(x=current_x, y=0, relheight=1, width=self.width)
            self.panel.update()

            if (start_x < end_x <= current_x) or (start_x > end_x >= current_x):
                break

        # Ensure final position is exact
        self.panel.place(x=end_x, y=0, relheight=1, width=self.width)

    def slideOut(self, start_x, end_x):
        """Animate the panel sliding out from start_x to end_x"""
        for i in range(0, abs(end_x - start_x) + 1, 10):
            if start_x < end_x:  # Sliding right
                current_x = start_x + i
            else:  # Sliding left
                current_x = start_x - i

            self.panel.place(x=current_x, y=0, relheight=1, width=self.width)
            self.panel.update()

        self.panel.place_forget()

    def menuItemClicked(self, item):
        """Default menu item click handler - override in subclasses"""
        # Notify parent that an action was executed
        if self.onActionExecuted:
            self.onActionExecuted()
        item.invokeFn()
