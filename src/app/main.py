import os
import sys

try:
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
except KeyError:
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    sys.path = [
        '/usr/lib/python3.10',
        '/usr/lib/python3.10/lib-dynload',
        '/usr/local/lib/python3.10/dist-packages',
        '/usr/lib/python3/dist-packages',
        '.',
        '../..',
    ]

import matplotlib as mpl

from src.resources.version import Version
from src.app.ui_manager.root_manager import RootManager
from src.app.main_shared.main_shared import MainShared


class Main(MainShared):
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
