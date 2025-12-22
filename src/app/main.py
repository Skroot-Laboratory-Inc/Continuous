import logging
import traceback

import matplotlib as mpl

from src.app.common_modules.common_modules import CommonModules
from src.app.helper_methods.file_manager.common_file_manager import CommonFileManager
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.theme_manager import ThemeManager
from src.app.widget import logger
from src.resources.version.version import Version


class Main(CommonModules):
    def __init__(self):
        version = Version()
        ThemeManager().set_theme(version.getTheme())

        self.GuiManager = RootManager()
        logger.loggerSetup(
            f"{CommonFileManager().getExperimentLogDir()}/log.txt",
            f"{version.getUseCase()}: v{version.getVersionString()}",
        )
        try:
            super().__init__(self.GuiManager)
        except:
            logging.exception("Exception in Main Initialization", extra={"id": "System failure"})
            tb = traceback.format_exc()
            try:
                self.GuiManager.showErrorPage("Initialization failed", tb)
            except Exception:
                logging.exception("Failed to display error page", extra={"id": "UI failure"})
        finally:
            self.GuiManager.callMainLoop()


mpl.use('TkAgg')
Main()
