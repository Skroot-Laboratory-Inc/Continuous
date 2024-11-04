import logging
import tkinter as tk
from importlib.metadata import version as version_api
from tkinter import messagebox

from reactivex.subject import BehaviorSubject

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper.helper_functions import getOperatingSystem
from src.app.main_shared.initialization.setup_base_ui import SetupBaseUi
from src.app.main_shared.thread_manager.reader_page_thread_manager import ReaderPageThreadManager
from src.app.model.setup_reader_form_input import SetupReaderFormInput
from src.app.properties.dev_properties import DevProperties
from src.app.properties.gui_properties import GuiProperties
from src.app.ui_manager.reader_page_manager import ReaderPageManager
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import logger


class MainShared:
    def __init__(self, rootManager: RootManager, version, major_version, minor_version):
        self.CommonFileManager = CommonFileManager()
        logger.loggerSetup(self.CommonFileManager.getExperimentLog(), version)
        logging.info(f'Sibcontrol version: {version_api("sibcontrol")}', extra={"id": "global"})

        self.mainFreqToggleSet = BehaviorSubject("Signal Check")
        self.RootManager = rootManager
        self.ReaderPageManager = ReaderPageManager(rootManager)
        self.guidedSetupForm = SetupReaderFormInput()
        self.configureRoot()
        self.bodyFrame = SetupBaseUi(self.RootManager, major_version, minor_version).bodyFrame
        self.isDevMode = DevProperties().isDevMode
        self.createReadersUi()

    def configureRoot(self):
        operatingSystem = getOperatingSystem()
        self.RootManager.setProtocol("WM_DELETE_WINDOW", self.onClosing)
        if operatingSystem == 'windows':
            self.RootManager.setState('zoomed')
        elif operatingSystem == 'linux':
            self.RootManager.setFullscreen()
            self.RootManager.setAttribute('-zoomed', True)

        def _create_circle(this, x, y, r, **kwargs):
            return this.create_oval(x - r, y - r, x + r, y + r, **kwargs)

        tk.Canvas.create_circle = _create_circle

    def createReadersUi(self):
        readersPerScreen = GuiProperties().readersPerScreen
        numScreens = GuiProperties().numScreens
        self.ReaderPageManager.createPages(numScreens)

        for screenNumber in range(0, numScreens):
            readerPage = self.ReaderPageManager.getPage(screenNumber)
            startingReaderNumber = 1 + screenNumber*readersPerScreen
            finalReaderNumber = startingReaderNumber + readersPerScreen
            ReaderPageThreadManager(
                readerPage,
                startingReaderNumber,
                finalReaderNumber,
                self.mainFreqToggleSet,
                self.RootManager,
            )

            self.ReaderPageManager.createNextAndPreviousFrameButtons()
            self.ReaderPageManager.showPage(self.ReaderPageManager.getPage(0))

    def onClosing(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to close the program?"):
            self.RootManager.destroyRoot()
