# python
import logging
import platform
import threading
import tkinter as tk
from tkinter import ttk

from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.common_modules.wifi.helpers.wifi_helpers import (
    checkInternetConnection,
    getWifiNetworks,
    connectToWifi,
    disconnectWifi,
    checkAndAuthenticateCaptivePortal
)
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, formatPopup, launchKeyboard
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme


class ConnectivityPopup:
    """
    Popup window for managing WiFi network connections.
    Displays available networks and allows connecting/disconnecting.
    """

    def __init__(self, rootManager: RootManager, connectivityButton=None):
        self.rootManager = rootManager
        self.connectivityButton = connectivityButton
        self.networks = []
        self.selectedNetwork = None
        self.isRefreshing = False
        self.password = tk.StringVar()
        self.username = tk.StringVar()
        self.authMethod = tk.StringVar(value='peap')
        self.showPassword = tk.BooleanVar(value=False)
        self.windowRoot = rootManager.createTopLevel()
        formatPopup(self.windowRoot)
        self.windowRoot.transient(rootManager.getRoot())
        self.createHeader()
        self.statusLabel = self.createStatusSection()
        self.networkListbox = self.createNetworkList()
        self.usernameFrame, self.usernameEntry = self.createUsernameSection()
        self.passwordFrame, self.passwordEntry, self.showPasswordButton = self.createPasswordSection()
        self.authMethodFrame, self.authMethodDropdown = self.createAuthMethodSection()
        self.refreshButton, self.connectButton, self.disconnectButton, self.portalAuthButton = self.createButtonSection()
        self.refreshNetworks()
        self.updateConnectionStatus()

        centerWindowOnFrame(self.windowRoot, self.rootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)

    def createHeader(self):
        headerFrame = tk.Frame(self.windowRoot, background=Colors().body.background)
        headerFrame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        ttk.Label(
            headerFrame,
            text="Network Connections",
            font=FontTheme().header1,
            background=Colors().body.background,
            foreground=Colors().body.text
        ).pack(side=tk.LEFT)

        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, sticky='ew', pady=5
        )

    def createStatusSection(self):
        statusFrame = tk.Frame(self.windowRoot, background=Colors().body.background)
        statusFrame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)

        ttk.Label(
            statusFrame,
            text="Status:",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text
        ).pack(side=tk.LEFT, padx=(0, 5))

        statusLabel = ttk.Label(
            statusFrame,
            text="Checking...",
            font=FontTheme().primary2,
            background=Colors().body.background,
            foreground=Colors().body.text,
            wraplength=statusFrame.winfo_width() - 40,
            justify=tk.LEFT,
            anchor='w'
        )
        statusLabel.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return statusLabel

    def createNetworkList(self):
        listFrame = ttk.Frame(self.windowRoot)
        listFrame.grid(row=3, column=0, sticky='nsew', padx=10, pady=5)
        self.windowRoot.grid_rowconfigure(3, weight=1)
        self.windowRoot.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(listFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        networks = tk.Listbox(
            listFrame,
            font=FontTheme().primary2,
            bg=Colors().body.background,
            fg=Colors().body.text,
            selectbackground=Colors().buttons.background,
            selectforeground=Colors().buttons.text,
            yscrollcommand=scrollbar.set,
            selectborderwidth=10,
            relief=tk.SUNKEN,
            height=5,
            activestyle='none',
            highlightthickness=0,
        )
        networks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=networks.yview)

        networks.bind('<<ListboxSelect>>', self.onNetworkSelect)
        networks.bind('<Double-Button-1>', lambda e: self.connectToSelectedNetwork())
        return networks

    def createUsernameSection(self):
        # Username frame is hidden by default; shown for enterprise networks
        frame = tk.Frame(self.windowRoot, background=Colors().body.background)
        frame.grid(row=4, column=0, sticky='ew', padx=10, pady=(0, 5))
        ttk.Label(
            frame,
            text="Username:",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text
        ).pack(side=tk.LEFT, padx=(0, 5))

        usernameEntry = ttk.Entry(
            frame,
            textvariable=self.username,
            font=FontTheme().primary2
        )
        usernameEntry.bind(
            "<Button-1>",
            lambda event: launchKeyboard(event.widget, self.rootManager.getRoot(), "Username:  ")
        )
        usernameEntry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=WidgetTheme().externalPadding, pady=WidgetTheme().externalPadding)
        frame.grid_remove()
        return frame, usernameEntry

    def createPasswordSection(self):
        # Password frame is hidden by default; shown for secured networks
        frame = tk.Frame(self.windowRoot, background=Colors().body.background)
        frame.grid(row=5, column=0, sticky='ew', padx=10, pady=(0, 5))
        ttk.Label(
            frame,
            text="Password:",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text
        ).pack(side=tk.LEFT, padx=(0, 5))

        passwordEntry = ttk.Entry(
            frame,
            textvariable=self.password,
            show='*',
            font=FontTheme().primary2
        )
        passwordEntry.bind(
            "<Button-1>",
            lambda event: launchKeyboard(event.widget, self.rootManager.getRoot(), "Password:  ", hidePassword=True)
        )
        passwordEntry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=WidgetTheme().externalPadding, pady=WidgetTheme().externalPadding)

        def toggle_show():
            self.passwordEntry.configure(show='' if self.showPassword.get() else '*')

        showPasswordButton = ttk.Checkbutton(
            frame,
            text="Show",
            variable=self.showPassword,
            command=toggle_show,
            style='Entry.TButton'
        )
        showPasswordButton.pack(side=tk.LEFT)
        frame.grid_remove()
        return frame, passwordEntry, showPasswordButton

    def createAuthMethodSection(self):
        # Auth method frame is hidden by default; shown for enterprise networks
        frame = tk.Frame(self.windowRoot, background=Colors().body.background)
        frame.grid(row=6, column=0, sticky='ew', padx=10, pady=(0, 5))
        ttk.Label(
            frame,
            text="Auth Method:",
            font=FontTheme().primary,
            background=Colors().body.background,
            foreground=Colors().body.text
        ).pack(side=tk.LEFT, padx=(0, 5))

        auth_methods = [
            ('PEAP (MSCHAPv2)', 'peap'),
            ('TTLS (MSCHAPv2)', 'ttls'),
            ('TLS (Certificate)', 'tls'),
            ('FAST', 'fast'),
            ('PWD', 'pwd'),
            ('LEAP', 'leap')
        ]

        authMethodDropdown = ttk.Combobox(
            frame,
            textvariable=self.authMethod,
            values=[method[0] for method in auth_methods],
            state='readonly',
            font=FontTheme().primary2,
            width=20
        )
        authMethodDropdown.set('PEAP (MSCHAPv2)')  # Default
        authMethodDropdown.pack(side=tk.LEFT, padx=WidgetTheme().externalPadding, pady=WidgetTheme().externalPadding)
        frame.grid_remove()
        return frame, authMethodDropdown

    def createButtonSection(self):
        buttonFrame = tk.Frame(self.windowRoot, background=Colors().body.background)
        buttonFrame.grid(row=7, column=0, sticky='ew', padx=10, pady=10)

        refreshButton = GenericButton(
            "Refresh",
            buttonFrame,
            self.refreshNetworks
        ).button
        refreshButton.pack(side=tk.LEFT, padx=5)

        connectButton = GenericButton(
            "Connect",
            buttonFrame,
            self.connectToSelectedNetwork
        ).button
        connectButton.pack(side=tk.LEFT, padx=5)
        connectButton.configure(state="disabled")

        portalAuthButton = GenericButton(
            "Auth Portal",
            buttonFrame,
            self.authenticatePortal
        ).button
        portalAuthButton.pack(side=tk.LEFT, padx=5)

        closeButton = GenericButton(
            "Close",
            buttonFrame,
            self.close
        ).button
        closeButton.pack(side=tk.RIGHT, padx=5)

        disconnectButton = GenericButton(
            "Disconnect",
            buttonFrame,
            self.disconnectFromNetwork
        ).button
        disconnectButton.pack(side=tk.RIGHT, padx=5)
        return refreshButton, connectButton, disconnectButton, portalAuthButton

    def updateConnectionStatus(self):
        def checkStatus():
            connected = checkInternetConnection(timeout=2)
            status_text = "Connected to Internet" if connected else "No Internet Connection"
            color = Colors().status.success if connected else Colors().status.error

            # Update UI in main thread
            self.windowRoot.after(0, lambda: self.statusLabel.configure(
                text=status_text,
                foreground=color
            ))

        thread = threading.Thread(target=checkStatus, daemon=True)
        thread.start()

    def refreshNetworks(self):
        """Refresh the list of available networks"""
        if self.isRefreshing:
            return

        self.isRefreshing = True
        self.refreshButton.configure(state="disabled", text="Refreshing...")
        self.connectButton.configure(state="disabled")
        self.disconnectButton.configure(state="disabled")

        def loadNetworks():
            try:
                networks = getWifiNetworks()

                # Update UI in main thread
                def updateUI():
                    self.networks = networks
                    self.networkListbox.delete(0, tk.END)

                    if not networks:
                        self.networkListbox.insert(tk.END, "No networks found")
                    else:
                        for network in networks:
                            display = f"{network['ssid']}"
                            if network['in_use']:
                                display += " ✓"
                            if network.get('is_enterprise', False):
                                display += " [Enterprise]"
                            self.networkListbox.insert(tk.END, display)

                    self.refreshButton.configure(state="normal", text="Refresh")
                    self.disconnectButton.configure(state="normal")
                    self.isRefreshing = False
                    self.updateConnectionStatus()

                self.windowRoot.after(0, updateUI)

            except Exception as e:
                logging.exception("Error refreshing networks", extra={"id": "Network"})
                self.windowRoot.after(0, lambda: self.refreshButton.configure(
                    state="normal", text="Refresh"
                ))
                self.isRefreshing = False

        thread = threading.Thread(target=loadNetworks, daemon=True)
        thread.start()

    def onNetworkSelect(self, event):
        """Handle network selection"""
        selection = self.networkListbox.curselection()
        if selection and self.networks:
            index = selection[0]
            if 0 <= index < len(self.networks):
                self.selectedNetwork = self.networks[index]
                security = self.selectedNetwork.get('security', 'Open')
                is_enterprise = self.selectedNetwork.get('is_enterprise', False)

                # Clear previous entries
                self.password.set('')
                self.username.set('')

                if security and security != 'Open':
                    if is_enterprise:
                        # Show enterprise fields (username, password, auth method)
                        self.usernameFrame.grid()
                        self.passwordFrame.grid()
                        self.authMethodFrame.grid()
                        self.windowRoot.after(50, lambda: self.usernameEntry.focus_set())
                    else:
                        # Show only password for WPA-PSK
                        self.usernameFrame.grid_remove()
                        self.passwordFrame.grid()
                        self.authMethodFrame.grid_remove()
                        self.windowRoot.after(50, lambda: self.passwordEntry.focus_set())
                else:
                    # Open network - hide all auth fields
                    self.usernameFrame.grid_remove()
                    self.passwordFrame.grid_remove()
                    self.authMethodFrame.grid_remove()

                self.connectButton.configure(state="normal")
            else:
                self.selectedNetwork = None
                self.usernameFrame.grid_remove()
                self.passwordFrame.grid_remove()
                self.authMethodFrame.grid_remove()
                self.connectButton.configure(state="disabled")
        else:
            self.selectedNetwork = None
            self.usernameFrame.grid_remove()
            self.passwordFrame.grid_remove()
            self.authMethodFrame.grid_remove()
            self.connectButton.configure(state="disabled")

    def connectToSelectedNetwork(self):
        """Connect to the selected network"""
        if not self.selectedNetwork:
            return

        ssid = self.selectedNetwork['ssid']
        security = self.selectedNetwork.get('security')
        is_enterprise = self.selectedNetwork.get('is_enterprise', False)

        # Read credentials from entries if required
        password = None
        username = None
        auth_method = None

        if security != 'Open':
            password = self.password.get()
            if not password:
                # If empty, show error message in status and don't attempt connect
                self.statusLabel.configure(
                    text="Password required",
                    foreground=Colors().status.error
                )
                return

            # For enterprise networks, also get username and auth method
            if is_enterprise:
                username = self.username.get()
                if not username:
                    self.statusLabel.configure(
                        text="Username required for enterprise network",
                        foreground=Colors().status.error
                    )
                    return

                # Map the displayed auth method back to the value
                auth_method_map = {
                    'PEAP (MSCHAPv2)': 'peap',
                    'TTLS (MSCHAPv2)': 'ttls',
                    'TLS (Certificate)': 'tls',
                    'FAST': 'fast',
                    'PWD': 'pwd',
                    'LEAP': 'leap'
                }
                selected_method = self.authMethodDropdown.get()
                auth_method = auth_method_map.get(selected_method, 'peap')

        # Disable buttons during connection
        self.connectButton.configure(state="disabled", text="Connecting...")
        self.disconnectButton.configure(state="disabled")
        self.refreshButton.configure(state="disabled")

        def connect():
            try:
                success, message = connectToWifi(ssid, password, username, auth_method)

                def updateUI():
                    if success:
                        self.statusLabel.configure(
                            text=message,
                            foreground=Colors().status.success
                        )
                        if self.connectivityButton:
                            self.connectivityButton.forceCheck()
                        self.windowRoot.after(1000, self.refreshNetworks)
                    else:
                        self.statusLabel.configure(
                            text=message,
                            foreground=Colors().status.error
                        )

                    self.connectButton.configure(state="normal", text="Connect")
                    self.disconnectButton.configure(state="normal")
                    self.refreshButton.configure(state="normal")

                self.windowRoot.after(0, updateUI)

            except Exception as e:
                logging.exception("Error connecting to network", extra={"id": "Network"})
                self.windowRoot.after(0, lambda: self.connectButton.configure(
                    text="Connect"
                ))
                self.windowRoot.after(0, lambda: self.disconnectButton.configure(
                    state="normal"
                ))
                self.windowRoot.after(0, lambda: self.refreshButton.configure(
                    state="normal"
                ))

        thread = threading.Thread(target=connect, daemon=True)
        thread.start()

    def disconnectFromNetwork(self):
        """Disconnect from the current network"""
        self.disconnectButton.configure(state="disabled", text="Disconnecting...")
        self.connectButton.configure(state="disabled")
        self.refreshButton.configure(state="disabled")

        def disconnect():
            try:
                success, message = disconnectWifi()

                def updateUI():
                    self.statusLabel.configure(
                        text=message,
                        foreground=Colors().status.success if success else Colors().status.error
                    )

                    if success:
                        if self.connectivityButton:
                            self.connectivityButton.forceCheck()
                        self.windowRoot.after(1000, self.refreshNetworks)

                    self.disconnectButton.configure(state="normal", text="Disconnect")
                    self.refreshButton.configure(state="normal")

                self.windowRoot.after(0, updateUI)

            except Exception as e:
                logging.exception("Error disconnecting from network", extra={"id": "Network"})
                self.windowRoot.after(0, lambda: self.disconnectButton.configure(
                    state="normal", text="Disconnect"
                ))
                self.windowRoot.after(0, lambda: self.connectButton.configure(
                    state="normal"
                ))
                self.windowRoot.after(0, lambda: self.refreshButton.configure(
                    state="normal"
                ))

        thread = threading.Thread(target=disconnect, daemon=True)
        thread.start()

    def authenticatePortal(self):
        """Manually authenticate with captive portal using stored credentials"""
        username = self.username.get()
        password = self.password.get()

        if not username or not password:
            self.statusLabel.configure(
                text="Username and password required for portal authentication",
                foreground=Colors().status.error
            )
            return

        self.portalAuthButton.configure(state="disabled", text="Authenticating...")
        self.connectButton.configure(state="disabled")
        self.refreshButton.configure(state="disabled")
        self.disconnectButton.configure(state="disabled")

        def authenticate():
            try:
                success, message = checkAndAuthenticateCaptivePortal(username, password)

                def updateUI():
                    self.statusLabel.configure(
                        text=message,
                        foreground=Colors().status.success if success else Colors().status.error
                    )

                    if success and self.connectivityButton:
                        self.connectivityButton.forceCheck()

                    self.portalAuthButton.configure(state="normal", text="Auth Portal")
                    self.connectButton.configure(state="normal")
                    self.refreshButton.configure(state="normal")
                    self.disconnectButton.configure(state="normal")

                self.windowRoot.after(0, updateUI)

            except Exception as e:
                logging.exception("Error authenticating with captive portal", extra={"id": "Network"})
                self.windowRoot.after(0, lambda: self.portalAuthButton.configure(
                    state="normal", text="Auth Portal"
                ))
                self.windowRoot.after(0, lambda: self.connectButton.configure(
                    state="normal"
                ))
                self.windowRoot.after(0, lambda: self.refreshButton.configure(
                    state="normal"
                ))
                self.windowRoot.after(0, lambda: self.disconnectButton.configure(
                    state="normal"
                ))

        thread = threading.Thread(target=authenticate, daemon=True)
        thread.start()

    def close(self):
        """Close the popup"""
        self.windowRoot.destroy()
