import platform
from tkinter import ttk

from src.app.helper_methods.custom_exceptions.common_exceptions import UserConfirmationException
from src.app.use_case.flow_cell.pump.pump_manager import PumpManager
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.helper_methods.ui_helpers import centerWindowOnFrame, formatPopup
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.widget_theme import WidgetTheme
from src.app.widget.pump_toggle_widget import PumpToggleWidget


class PumpControlPopup:
    def __init__(self, rootManager: RootManager, header: str, message: str, pumpManager: PumpManager,
                 altCancelText: str = "Cancel", altContinueText: str = "Continue",
                 requireConfirmation: bool = True):
        """
        Ask the user to confirm an action while allowing pump control.
        :param rootManager: The RootManager to create the toplevel from.
        :param header: The header for the dialog box
        :param message: The message to display (e.g., "Would you like to prime the line?")
        :param pumpManager: The PumpManager for pump control
        :param altCancelText: The text to display on the "Cancel" button
        :param altContinueText: The text to display on the "Continue" button
        :param requireConfirmation: If False, closing/canceling will not raise UserConfirmationException

        :raises UserConfirmationException: if the user cancels the action and requireConfirmation is True
        """
        self.confirmed = False
        self.requireConfirmation = requireConfirmation
        self.RootManager = rootManager
        self.pumpManager = pumpManager
        self.pumpManager.setPriming(True)
        self.windowRoot = rootManager.createTopLevel()
        formatPopup(self.windowRoot)
        self.windowRoot.transient(rootManager.getRoot())

        self.createHeader(header)
        self.createMessage(message)
        self.pumpToggleWidget = PumpToggleWidget(self.windowRoot, pumpManager)
        self.pumpToggleWidget.getWidget().grid(row=4, column=0, columnspan=3, pady=WidgetTheme().externalPadding)
        self.cancelButton = self.createCancelButton(altCancelText)
        self.continueButton = self.createContinueButton(altContinueText)

        centerWindowOnFrame(self.windowRoot, self.RootManager.getRoot())
        if platform.system() == "Windows":
            self.windowRoot.overrideredirect(True)
            self.windowRoot.attributes('-topmost', True)
        rootManager.waitForWindow(self.windowRoot)
        self.pumpManager.setPriming(False)
        self.getConfirm()

    def createHeader(self, header: str):
        ttk.Label(
            self.windowRoot,
            text=header,
            font=FontTheme().header1,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=0, column=0, columnspan=3)
        ttk.Separator(self.windowRoot, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', pady=WidgetTheme().externalPadding)

    def createMessage(self, message: str):
        ttk.Label(
            self.windowRoot,
            text=message,
            font=FontTheme().primary2,
            background=Colors().body.background,
            foreground=Colors().body.text).grid(row=3, column=0, columnspan=3, pady=WidgetTheme().externalPadding)

    def createContinueButton(self, text: str):
        continueButton = GenericButton(text, self.windowRoot, self.confirm).button
        continueButton.grid(row=6, column=1, pady=WidgetTheme().externalPadding, padx=WidgetTheme().internalPadding, columnspan=2, sticky="e")
        return continueButton

    def createCancelButton(self, text: str):
        cancelButton = GenericButton(text, self.windowRoot, self.cancel).button
        cancelButton.grid(row=6, column=0, pady=WidgetTheme().externalPadding, padx=WidgetTheme().internalPadding, sticky="w")
        return cancelButton

    def confirm(self):
        self.confirmed = True
        try:
            self.pumpManager.stop()
            self.pumpToggleWidget.cleanup()
        finally:
            self.windowRoot.destroy()

    def cancel(self):
        self.confirmed = False
        try:
            self.pumpManager.stop()
            self.pumpToggleWidget.cleanup()
        finally:
            self.windowRoot.destroy()

    def getConfirm(self):
        if self.confirmed:
            pass
        elif self.requireConfirmation:
            raise UserConfirmationException()
        else:
            pass  # Just close without exception
