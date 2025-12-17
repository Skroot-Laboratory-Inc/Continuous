import platform
import tkinter as tk

from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.common_modules.initialization.setup_base_ui import SetupBaseUi
from src.app.helper_methods.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.reader_page_manager import ReaderPageManager
from src.app.ui_manager.root_manager import RootManager


class CommonModules:
    def __init__(self, rootManager: RootManager, major_version, minor_version):
        self.CommonFileManager = CommonFileManager()
        self.RootManager = rootManager
        self.sessionManager = SessionManager()
        self.bodyFrame = SetupBaseUi(self.RootManager, self.sessionManager, major_version, minor_version).bodyFrame
        self.ReaderPageManager = ReaderPageManager(self.bodyFrame, rootManager, self.sessionManager)
        self.configureRoot()
        self.ReaderPageManager.createPages()

    def configureRoot(self):
        if platform.system() == 'Windows':
            self.RootManager.setOverrideRedirect()
        elif platform.system() == 'Linux':
            self.RootManager.setAttribute('-zoomed', True)
        self.RootManager.setWindowSize()

        def _create_circle(this, x, y, r, **kwargs):
            return this.create_oval(x - r, y - r, x + r, y + r, **kwargs)

        tk.Canvas.create_circle = _create_circle
