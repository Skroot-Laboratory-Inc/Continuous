import matplotlib as mpl

from src.app.common_modules.common_modules import CommonModules
from src.app.ui_manager.root_manager import RootManager
from src.resources.version.version import Version


class Main(CommonModules):
    def __init__(self):
        self.GuiManager = RootManager()
        version = Version()
        super().__init__(
            self.GuiManager,
            f"Version: Cell_v{version.getMajorVersion()}.{version.getMinorVersion()}",
            version.getMajorVersion(),
            version.getMinorVersion(),
        )
        self.GuiManager.callMainLoop()


mpl.use('TkAgg')
Main()
