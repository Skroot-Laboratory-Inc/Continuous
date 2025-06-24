import platform
import tkinter as tk

from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.common_modules.initialization.setup_base_ui import SetupBaseUi
from src.app.common_modules.thread_manager.reader_page_thread_manager import ReaderPageThreadManager
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.properties.dev_properties import DevProperties
from src.app.properties.gui_properties import GuiProperties
from src.app.ui_manager.reader_page_manager import ReaderPageManager
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import logger


class CommonModules:
    def __init__(self, rootManager: RootManager, version, major_version, minor_version):
        self.CommonFileManager = CommonFileManager()
        logger.loggerSetup(self.CommonFileManager.getExperimentLog(), version)
        self.RootManager = rootManager
        self.sessionManager = SessionManager()
        self.bodyFrame = SetupBaseUi(self.RootManager, self.sessionManager, major_version, minor_version).bodyFrame
        self.ReaderPageManager = ReaderPageManager(self.bodyFrame)
        self.configureRoot()
        self.isDevMode = DevProperties().isDevMode
        self.createReadersUi()

    def configureRoot(self):
        if platform.system() == 'Windows':
            self.RootManager.setWindowSize()
        elif platform.system() == 'Linux':
            self.RootManager.setFullscreen()
            self.RootManager.setAttribute('-zoomed', True)

        def _create_circle(this, x, y, r, **kwargs):
            return this.create_oval(x - r, y - r, x + r, y + r, **kwargs)

        tk.Canvas.create_circle = _create_circle

    def createReadersUi(self):
        numScreens = GuiProperties().numScreens
        self.ReaderPageManager.createPages(numScreens)

        for screenNumber in range(0, numScreens):
            readerPage = self.ReaderPageManager.getPage(screenNumber)
            startingReaderNumber = 1 + screenNumber
            ReaderPageThreadManager(
                readerPage,
                startingReaderNumber,
                self.RootManager,
                self.sessionManager,
            )
            self.ReaderPageManager.showPage(self.ReaderPageManager.getPage(0))
