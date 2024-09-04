import logging
import tkinter as tk
from importlib.metadata import version as version_api

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.main_shared.service.aws_service import AwsService
from src.app.main_shared.service.dev_aws_service import DevAwsService
from src.app.ui_manager.root_manager import RootManager
from src.app.helper.helper_functions import getOperatingSystem
from src.app.main_shared.end_of_experiment_view import EndOfExperimentView
from src.app.main_shared.initialization.buttons import ButtonFunctions
from src.app.main_shared.initialization.settings import Settings
from src.app.main_shared.initialization.setup_gui import SetupGui
from src.app.main_shared.reader_threads.main_thread_manager import MainThreadManager
from src.app.model.guided_setup_input import GuidedSetupInput
from src.app.properties.common_properties import CommonProperties
from src.app.properties.dev_properties import DevProperties
from src.app.reader.helpers.experiment_notes import ExperimentNotes
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.theme.color_cycler import ColorCycler
from src.app.theme.colors import Colors
from src.app.widget import logger
from src.app.widget.figure import FigureCanvas
from src.app.widget.guided_setup import SetupForm


class MainShared:
    def __init__(self, rootManager: RootManager, version, major_version, minor_version):
        self.RootManager = rootManager
        self.major_version = major_version
        self.minor_version = minor_version
        self.foundPorts = False
        self.guidedSetupForm = GuidedSetupInput()
        self.Properties = CommonProperties()
        self.CommonFileManager = CommonFileManager()
        self.Colors = Colors()
        self.startFreq = self.Properties.defaultStartFrequency
        self.stopFreq = self.Properties.defaultEndFrequency
        logger.loggerSetup(self.CommonFileManager.getExperimentLog(), version)
        logging.info(f'Sibcontrol version: {version_api("sibcontrol")}')
        self.version = f'{major_version}.{minor_version}'
        self.denoiseSet = True
        self.disableSaveFullFiles = False
        self.primaryColor = self.Colors.primaryColor
        self.secondaryColor = self.Colors.secondaryColor
        self.PortAllocator = PortAllocator()
        self.createRoot()
        self.ColorCycler = ColorCycler()
        self.Readers = []
        self.Settings = Settings(self, self.RootManager)
        self.Setup = SetupGui(self.RootManager, self.Settings, self)
        self.bodyFrame = self.Setup.createFrames()
        self.isDevMode = DevProperties().isDevMode
        self.SummaryFigureCanvas = FigureCanvas(
            'k',
            'Skroot Growth Index (SGI)',
            'Time (hrs)',
            self.secondaryColor,
            'Summary',
            ''
        )
        self.Buttons = ButtonFunctions(self, self.RootManager, self.PortAllocator)
        self.createGuidedSetup()
        if self.isDevMode:
            self.AwsService = DevAwsService(self.RootManager, major_version, minor_version, self.GlobalFileManager)
        else:
            self.AwsService = AwsService(self.RootManager, major_version, minor_version, self.GlobalFileManager)
        self.MainThreadManager = MainThreadManager(
            self.denoiseSet,
            self.disableSaveFullFiles,
            self.RootManager,
            self.AwsService,
            self.GlobalFileManager,
            self.bodyFrame,
            self.SummaryFigureCanvas,
            self.resetRun,
            self.guidedSetupForm,
        )
        self.ExperimentNotes = ExperimentNotes(self.GlobalFileManager)
        self.Buttons.MainThreadManager = self.MainThreadManager
        self.Buttons.createButtonsOnNewFrame()
        self.menubar = self.createMenubarOptions()

    def createMenubarOptions(self):
        menubar = self.Setup.createMenus()
        self.RootManager.addMenubar(menubar)
        return menubar

    def createGuidedSetup(self):
        self.guidedSetup()
        self.Buttons.createGuidedSetupButton(self.RootManager.getRoot())
        self.Buttons.HelpButton.place()

    def guidedSetup(self):
        self.destroyExistingWidgets()
        self.bodyFrame.tkraise()
        setupForm = SetupForm(self.RootManager, self.guidedSetupForm)
        self.guidedSetupForm, self.GlobalFileManager = setupForm.getConfiguration()
        self.resetMainThreadManager()
        self.RootManager.raiseRoot()
        self.Buttons.createButtonsOnNewFrame()
        self.Buttons.placeConnectReadersButton()
        if self.guidedSetupForm.getCalibrate():
            self.foundPorts = True
            if not self.isDevMode:
                self.Buttons.ConnectReadersButton.destroySelf()
                self.Buttons.findReaders(self.guidedSetupForm.getNumReaders(), self.GlobalFileManager)
                self.Buttons.placeCalibrateReadersButton()

    def resetMainThreadManager(self):
        try:
            self.MainThreadManager.GlobalFileManager = self.GlobalFileManager
            self.MainThreadManager.guidedSetupForm = self.guidedSetupForm
            self.MainThreadManager.scanRate = self.guidedSetupForm.getScanRate()
            self.MainThreadManager.equilibrationTime = self.guidedSetupForm.getEquilibrationTime()
        except:
            # New experiment, doesn't need reset
            pass

    def destroyExistingWidgets(self):
        try:
            self.Buttons.GuidedSetupButton.destroySelf()
            for widgets in self.endOfExperimentFrame.winfo_children():
                widgets.destroy()
            self.endOfExperimentFrame.destroy()
        except:
            # New experiment, nothing to destroy
            pass

    def createRoot(self):
        operatingSystem = getOperatingSystem()
        if operatingSystem == 'windows':
            self.RootManager.setState('zoomed')
        elif operatingSystem == 'linux':
            self.RootManager.setAttribute('-zoomed', True)

        def _create_circle(this, x, y, r, **kwargs):
            return this.create_oval(x - r, y - r, x + r, y + r, **kwargs)

        tk.Canvas.create_circle = _create_circle

    def resetRun(self):
        self.Settings.ReaderPageManager.resetPages()
        for widgets in self.bodyFrame.winfo_children():
            widgets.destroy()
        self.Buttons.IssueLog.clear()
        self.MainThreadManager.finalizeRunResults()
        self.displayReaderRunResults()
        self.MainThreadManager.freqToggleSet.on_completed()
        self.foundPorts = False
        self.Buttons.SibInterfaces = []
        self.Readers = []
        self.PortAllocator.resetPorts()
        self.RootManager.raiseRoot()
        self.ExperimentNotes = ExperimentNotes(self.GlobalFileManager)
        self.MainThreadManager = MainThreadManager(
            self.denoiseSet,
            self.disableSaveFullFiles,
            self.RootManager,
            self.AwsService,
            self.GlobalFileManager,
            self.bodyFrame,
            self.SummaryFigureCanvas,
            self.resetRun,
            self.guidedSetupForm,
        )
        self.Buttons.MainThreadManager = self.MainThreadManager

    def displayReaderRunResults(self):
        if self.MainThreadManager.finishedEquilibrationPeriod:
            endOfExperimentView = EndOfExperimentView(self.RootManager, self.GlobalFileManager)
            endOfExperimentFrame = endOfExperimentView.createEndOfExperimentView()
            self.Buttons.createGuidedSetupButton(endOfExperimentFrame)
            self.Buttons.GuidedSetupButton.place()
            self.SummaryFigureCanvas.frequencyCanvas = None
            self.endOfExperimentFrame = endOfExperimentFrame
        else:
            self.Buttons.createGuidedSetupButton(self.RootManager.getRoot())
            self.Buttons.GuidedSetupButton.invokeButton()
