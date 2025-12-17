import logging
import tkinter as tk
import threading

from PIL import Image, ImageTk

from src.app.helper_methods.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.image_theme import ImageTheme
from src.app.common_modules.wifi.helpers.wifi_helpers import checkInternetConnection
from src.app.common_modules.wifi.widget.connectivity_popup import ConnectivityPopup


class ConnectivityButton:
    """
    Button widget that displays internet connectivity status and allows network management.
    - Shows connected/disconnected icon
    - Automatically checks connectivity status every 10 seconds
    - Opens network popup when clicked
    """

    def __init__(self, master, rootManager: RootManager):
        self.rootManager = rootManager
        self.isConnected = False
        self.checkInterval = 10000  # Check every 10 seconds
        self.checking = False
        connectedImage = Image.open(CommonFileManager().getWifiConnectedIcon())
        disconnectedImage = Image.open(CommonFileManager().getWifiDisconnectedIcon())
        self.connectedIcon = ImageTk.PhotoImage(
            connectedImage.resize(ImageTheme().connectivitySize, Image.Resampling.LANCZOS)
        )
        self.disconnectedIcon = ImageTk.PhotoImage(
            disconnectedImage.resize(ImageTheme().connectivitySize, Image.Resampling.LANCZOS)
        )

        self.button = tk.Button(
            master,
            bg=Colors().header.background,
            highlightthickness=0,
            activebackground=Colors().header.background,
            borderwidth=0,
            padx=5,
            pady=0,
            image=self.disconnectedIcon,
            command=lambda: self.invoke()
        )

        self.startMonitoring()

    def invoke(self):
        """Open network management popup"""
        self.button.configure(state="disabled")
        try:
            ConnectivityPopup(self.rootManager, self)
        except Exception as e:
            logging.exception("Error opening connectivity popup", extra={"id": "Network"})
        finally:
            self.button.configure(state="normal")

    def startMonitoring(self):
        """Start periodic connectivity monitoring"""
        self.checkConnectivity()

    def checkConnectivity(self):
        """Check connectivity status and update icon"""
        if not self.checking:
            self.checking = True
            # Run check in background thread to avoid blocking UI
            thread = threading.Thread(target=self._performCheck, daemon=True)
            thread.start()

        # Schedule next check
        self.button.after(self.checkInterval, self.checkConnectivity)

    def _performCheck(self):
        """Perform actual connectivity check in background thread"""
        try:
            connected = checkInternetConnection(timeout=2)
            # Update UI in main thread
            self.button.after(0, lambda: self._updateStatus(connected))
        except Exception as e:
            logging.warning(f"Error checking connectivity: {e}", extra={"id": "Network"})
            self.button.after(0, lambda: self._updateStatus(False))
        finally:
            self.checking = False

    def _updateStatus(self, connected: bool):
        """Update button icon based on connectivity status (must be called from main thread)"""
        if connected != self.isConnected:
            self.isConnected = connected
            icon = self.connectedIcon if connected else self.disconnectedIcon
            try:
                self.button.configure(image=icon)
            except Exception as e:
                logging.warning(f"Error updating connectivity icon: {e}", extra={"id": "Network"})

    def forceCheck(self):
        """Force an immediate connectivity check"""
        self.checkConnectivity()

    def hide(self):
        """Hide the button"""
        self.button.configure(state="disabled")
        self.button.grid_remove()

    def show(self):
        """Show the button"""
        self.button.configure(state="normal")
        self.button.grid()
        self.button.tkraise()
