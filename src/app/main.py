import os
import sys

from src.app.widget.guided_setup import SetupForm

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
import importlib.util
import os
import json
from datetime import datetime

import matplotlib as mpl

from src.app.main_shared.main_shared import MainShared

mpl.use('TkAgg')


class Main(MainShared):
    def __init__(self, version, major_version, minor_version):
        super().__init__(version, major_version, minor_version)
        self.setupApp()
        self.root.mainloop()  # everything comes before this

    def setupApp(self):
        self.menubar = self.Setup.createMenus()
        self.root.config(menu=self.menubar)

        currentDate = datetime.now().date()
        self.guidedSetup(currentDate.month, currentDate.day, currentDate.year)
        self.Buttons.createGuidedSetupButton(self.readerPlotFrame)
        self.Buttons.placeHelpButton()
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            import pyi_splash
            pyi_splash.close()

    def guidedSetup(self, month=12, day=31, year=2023, numReaders="4", scanRate="5", cellType="Cell",
                    secondAxisTitle="", equilibrationTime="24"):
        try:
            self.Buttons.guidedSetupButton.destroy()
            for widgets in self.endOfExperimentFrame.winfo_children():
                widgets.destroy()
            self.endOfExperimentFrame.destroy()
        except:
            pass
        setupForm = SetupForm(self.root, month, day, year, numReaders, scanRate, cellType, secondAxisTitle, equilibrationTime)
        (self.month, self.day, self.year, self.savePath, self.numReaders, self.scanRate,
         calibrate, self.secondAxisTitle, self.cellType, self.equilibrationTime, self.GlobalFileManager) = setupForm.getConfiguration()
        self.Buttons.createButtonsOnNewFrame()
        self.Buttons.placeConnectReadersButton()
        if calibrate:
            self.foundPorts = True
            if not self.isDevMode:
                self.Buttons.connectReadersButton.destroy()
                self.Buttons.findReaders(self.numReaders)
                self.Buttons.placeCalibrateReadersButton()


with open('../resources/version.json') as j_file:
    version = json.load(j_file)

major_version = version['major_version']
minor_version = version['minor_version']
mpl.use('TkAgg')
Main(f"Version: Cell_v{major_version}.{minor_version}", major_version, minor_version)
