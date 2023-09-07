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
        self.foamingApp = False
        self.cellApp = True
        self.setupApp()
        self.root.mainloop()  # everything comes before this

    def setupApp(self):
        self.menubar = self.Setup.createMenus()
        self.Setup.createTheme()
        self.Setup.createFrames()
        self.root.config(menu=self.menubar)

        currentDate = datetime.now().date()
        self.guidedSetup(currentDate.month, currentDate.day, currentDate.year)
        self.Buttons.createGuidedSetupButton()
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            import pyi_splash
            pyi_splash.close()

    def guidedSetup(self, month=12, day=31, year=2023, numReaders=1, scanRate="1", cellType="Cell", vesselType="Vessel",
                    secondAxisTitle=""):
        (self.month, self.day, self.year, self.savePath, self.numReaders, self.scanRate, calibrate, self.cellType,
         self.vesselType, self.secondAxisTitle) = guided_setup.guidedSetupCell(self.root, self.baseSavePath, month, day,
                                                                               year, numReaders, scanRate, cellType,
                                                                               vesselType, secondAxisTitle)
        self.Buttons.createHelpButton(self.readerPlotFrame)
        self.Buttons.createConnectReadersButton()
        if calibrate:
            self.Buttons.connectReadersButton.destroy()
            self.foundPorts = True
            self.Buttons.calFunc2(self.numReaders, self)
            self.Buttons.createStartButton()


major_version = 1.1
minor_version = 1
AppModule(f"version: Cell_v{major_version}.{minor_version}", major_version, minor_version)
