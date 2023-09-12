import importlib.util
import os
from datetime import datetime

import matplotlib as mpl

import guided_setup
from main_shared import MainShared

mpl.use('TkAgg')


class AppModule(MainShared):
    def __init__(self, version, major_version, minor_version):
        super().__init__(version, major_version, minor_version)
        self.scanRate = 0.5
        self.startFreq = 40
        self.stopFreq = 250
        self.nPoints = 2000
        self.airFreq = 0
        self.waterFreq = 0
        self.waterShift = None
        self.cellApp = False
        self.foamingApp = True
        self.setupApp()
        self.root.mainloop()  # everything comes before this

    def setupApp(self):
        # TODO - update this to account for foaming setup, it will be different values needed
        self.Setup.createTheme()
        self.Setup.createFrames()
        self.menubar = self.Setup.createMenus()
        self.root.config(menu=self.menubar)

        self.Buttons.createConnectReadersButton()
        self.Buttons.createHelpButton(self.readerPlotFrame)
        currentDate = datetime.now().date()
        self.guidedSetup(currentDate.month, currentDate.day, currentDate.year)
        self.Buttons.createGuidedSetupButton()
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            import pyi_splash
            pyi_splash.close()

    def guidedSetup(self, month=12, day=31, year=2023, numReaders=1, scanRate="1", cellType="Cell",
                    vesselType="Vessel"):
        self.month, self.day, self.year, self.savePath, self.numReaders, self.scanRate, calibrate = \
            guided_setup.guidedSetupFoaming(self.root, self.baseSavePath, month, day, year, numReaders, scanRate,
                                            cellType, vesselType)
        if calibrate:
            self.Buttons.connectReadersButton.destroy()
            self.foundPorts = True
            self.Buttons.calFunc2(self.numReaders, self)
            self.Buttons.createStartButton()


major_version = 1.1
minor_version = 1
AppModule(f"version: Foaming_v{major_version}.{minor_version}")
