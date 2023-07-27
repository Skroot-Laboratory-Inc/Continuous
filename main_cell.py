import importlib.util
import os
import sys

import matplotlib as mpl

import guided_setup
import logger
import setup
from aws import AwsBoto3
from buttons import ButtonFunctions
from colors import ColorCycler
from dev import DevMode
from main_shared import MainShared
from server import ServerFileShare
from settings import Settings

mpl.use('TkAgg')


class AppModule(MainShared):
    def __init__(self, version):
        self.performedCalibration = False
        self.baseSavePath = None
        self.secondAxisTitle = None
        self.readerPlotFrame = None
        self.airFreqLabel = None
        self.waterFreqLabel = None
        self.currentFrame = None
        self.totalMin = None
        self.time = None
        self.frequency = None
        self.freq = None
        self.calFreq = None
        self.caldB = None
        self.calculatedCells = None
        self.dB = None
        self.notes = None
        self.viabilityTime = None
        self.totalViability = None
        self.summaryPlot = None
        self.summaryCanvas = None
        self.summaryFig = None
        self.summaryPlotButton = None
        self.summaryFrame = None
        self.submitButton = None
        self.waterFreqInput = None
        self.stopButton = None
        self.startButton = None
        self.airFreqInput = None
        self.menubar = None
        try:
            self.desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            self.os = 'windows'
        except:
            self.desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
            self.os = 'linux'
        logger.loggerSetup(f'{self.desktop}/Calibration/log.txt', version)
        self.numReaders = None
        self.savePath = ''
        self.cellApp = True
        self.foamingApp = False
        self.freqToggleSet = "Signal Check"
        self.splineToggleSet = False
        self.denoiseSet = True
        self.currentlyScanning = False
        self.disableSaveFullFiles = False
        self.emailSetting = False
        self.awsTimeBetweenUploads = 6
        self.awsLastUploadTime = 0
        self.scanRate = 0.5
        self.startFreq = 40
        self.stopFreq = 250
        self.nPoints = 2000
        self.airFreq = 0
        self.waterFreq = 0
        self.waterShift = None
        self.thread = ''
        self.threadStatus = ''
        self.royalBlue = 'RoyalBlue4'
        self.white = 'white'
        self.ports = []
        try:
            self.location = sys._MEIPASS
        except:
            self.location = os.getcwd()
        self.createRoot()
        self.ColorCycler = ColorCycler()
        self.ServerFileShare = ServerFileShare(self)
        self.Readers = []
        self.Settings = Settings(self)
        self.Buttons = ButtonFunctions(self)
        self.DevMode = DevMode()
        if not self.DevMode.isDevMode:
            self.aws = AwsBoto3()
        self.isDevMode = self.DevMode.isDevMode
        self.setupApp()
        self.root.mainloop()  # everything comes before this

    def setupApp(self):
        self.baseSavePath = self.desktop + "/data"
        if not os.path.exists(self.baseSavePath):
            os.mkdir(self.baseSavePath)
        self.Setup = setup.Setup(self.root, self.Buttons, self.Settings, self)
        self.menubar = self.Setup.createMenus()
        self.Setup.createTheme()
        self.Setup.createFrames()
        self.root.config(menu=self.menubar)

        self.savePath, self.numReaders, self.scanRate, calibrate, self.secondAxisTitle = \
            guided_setup.guidedSetupCell(self.root, self.baseSavePath)
        if calibrate:
            self.performedCalibration = True
            self.Buttons.calFunc(self.numReaders, self)
        self.Buttons.createStartButton()
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            import pyi_splash
            pyi_splash.close()


AppModule("version: Cell_v1.0.2")
