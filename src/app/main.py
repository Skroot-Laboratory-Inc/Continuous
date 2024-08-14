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
        '.'
    ]
import json

import matplotlib as mpl
import tkinter as tk

from src.app.main_shared.main_shared import MainShared


class Main(MainShared):
    def __init__(self, version, major_version, minor_version):
        root = tk.Tk()  # everything in the application comes after this
        super().__init__(root, version, major_version, minor_version)
        root.mainloop()  # everything comes before this


with open('../resources/version.json') as versionFile:
    _version = json.load(versionFile)

_major_version = _version['major_version']
_minor_version = _version['minor_version']
mpl.use('TkAgg')
Main(f"Version: Cell_v{_major_version}.{_minor_version}", _major_version, _minor_version)
