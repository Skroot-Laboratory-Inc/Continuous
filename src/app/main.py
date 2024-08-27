import os
import sys

from src.app.ui_manager.root_manager import RootManager

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
import json

import matplotlib as mpl

from src.app.main_shared.main_shared import MainShared


class Main(MainShared):
    def __init__(self, version, major_version, minor_version):
        self.GuiManager = RootManager()
        super().__init__(self.GuiManager, version, major_version, minor_version)
        self.GuiManager.callMainLoop()


with open('../resources/version.json') as versionFile:
    _version = json.load(versionFile)

_major_version = _version['major_version']
_minor_version = _version['minor_version']
mpl.use('TkAgg')
Main(f"Version: Cell_v{_major_version}.{_minor_version}", _major_version, _minor_version)
