import importlib.util
import os, json
import threading
from datetime import datetime

import matplotlib as mpl

import guided_setup
import text_notification
from main_shared import MainShared

mpl.use('TkAgg')


class AppModule(MainShared):
    def __init__(self, version, major_version, minor_version):
        super().__init__(version, major_version, minor_version)
        self.foamingApp = False
        self.cellApp = True
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
        except:
            pass
        (self.month, self.day, self.year, self.savePath, self.numReaders, self.scanRate, calibrate, self.cellType,
         self.secondAxisTitle, self.equilibrationTime) = guided_setup.guidedSetupCell(self.root, self.baseSavePath, month, day,
                                                                               year, numReaders, scanRate, cellType, secondAxisTitle, equilibrationTime)
        self.Buttons.createButtonsOnNewFrame()
        self.Buttons.placeConnectReadersButton()
        if calibrate:
            self.Buttons.connectReadersButton.destroy()
            self.foundPorts = True
            self.Buttons.findReaders(self.numReaders)
            self.Buttons.placeCalibrateReadersButton()


with open('./resources/version.json') as j_file:
    version = json.load(j_file)

major_version = version['major_version']
minor_version = version['minor_version']
AppModule(f"Version: Cell_v{major_version}.{minor_version}", major_version, minor_version)
