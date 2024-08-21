import logging
import tkinter as tk
from importlib.metadata import version as version_api

from reactivex.subject import BehaviorSubject

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper.helper_functions import getOperatingSystem
from src.app.main_shared.end_of_experiment_view import EndOfExperimentView
from src.app.main_shared.initialization.buttons import ButtonFunctions
from src.app.main_shared.initialization.settings import Settings
from src.app.main_shared.initialization.setup import Setup
from src.app.main_shared.reader_threads.main_thread_manager import MainThreadManager
from src.app.model.guided_setup_input import GuidedSetupInput
from src.app.properties.dev_properties import DevProperties
from src.app.properties.common_properties import CommonProperties
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.theme.color_cycler import ColorCycler
from src.app.theme.colors import Colors
from src.app.widget import logger
from src.app.widget.figure import FigureCanvas
from src.app.widget.guided_setup import SetupForm


class MainShared:
    def __init__(self, root, version, major_version, minor_version):
        self.root = root
        self.major_version = major_version
        self.minor_version = minor_version
        self.readerPlotFrame = None
        self.foundPorts = False
        self.currentFrame = None
        self.guidedSetupForm = GuidedSetupInput()
        self.Properties = CommonProperties()
        self.CommonFileManager = CommonFileManager()
        self.Colors = Colors()
        self.startFreq = self.Properties.defaultStartFrequency
        self.stopFreq = self.Properties.defaultEndFrequency
        logger.loggerSetup(self.CommonFileManager.getExperimentLog(), version)
        logging.info(f'Sibcontrol version: {version_api("sibcontrol")}')
        self.version = f'{major_version}.{minor_version}'
        self.freqToggleSet = BehaviorSubject("Signal Check")
        self.denoiseSet = True
        self.disableSaveFullFiles = False
        self.primaryColor = self.Colors.primaryColor
        self.secondaryColor = self.Colors.secondaryColor
        self.PortAllocator = PortAllocator()
        self.createRoot()
        self.ColorCycler = ColorCycler()
        self.Readers = []
        self.Settings = Settings(self)
        self.Setup = Setup(self.root, self.Settings, self)
        self.isDevMode = DevProperties().isDevMode
        self.SummaryFigureCanvas = FigureCanvas(
            'k',
            'Skroot Growth Index (SGI)',
            'Time (hrs)',
            self.secondaryColor,
            'Summary',
            '',
            7,
            9
        )
        self.Buttons = ButtonFunctions(self, self.root, self.PortAllocator)
        self.createGuidedSetup()
        self.MainThreadManager = MainThreadManager(
            self.denoiseSet,
            self.disableSaveFullFiles,
            root,
            major_version,
            minor_version,
            self.GlobalFileManager,
            self.readerPlotFrame,
            self.SummaryFigureCanvas,
            self.resetRun,
            self.guidedSetupForm,
        )
        self.Buttons.MainThreadManager = self.MainThreadManager
        self.Buttons.createButtonsOnNewFrame()
        self.menubar = self.createMenubarOptions()

    def createMenubarOptions(self):
        menubar = self.Setup.createMenus()
        self.root.config(menu=menubar)
        return menubar

    def createGuidedSetup(self):
        self.guidedSetup()
        self.Buttons.createGuidedSetupButton(self.readerPlotFrame)
        self.Buttons.HelpButton.place()

    def guidedSetup(self):
        self.destroyExistingWidgets()
        setupForm = SetupForm(self.root, self.guidedSetupForm)
        self.guidedSetupForm, self.GlobalFileManager = setupForm.getConfiguration()
        self.resetMainThreadManager()
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
            self.root.state('zoomed')
        elif operatingSystem == 'linux':
            self.root.attributes('-zoomed', True)

        def _create_circle(this, x, y, r, **kwargs):
            return this.create_oval(x - r, y - r, x + r, y + r, **kwargs)

        tk.Canvas.create_circle = _create_circle

    def showFrame(self, frame):
        self.currentFrame = frame
        try:
            frame.place(relx=0, rely=0.05, relwidth=1, relheight=0.9)
            frame.tkraise()
        except:
            logging.exception('Failed to change the frame visible')
        self.MainThreadManager.summaryFrame.tkraise()

    def resetRun(self):
        for widgets in self.readerPlotFrame.winfo_children():
            widgets.destroy()
        self.MainThreadManager.finalizeRunResults()
        self.displayReaderRunResults()
        self.freqToggleSet.on_completed()
        self.freqToggleSet = BehaviorSubject("Signal Check")
        self.foundPorts = False
        self.Buttons.SibInterfaces = []
        self.Readers = []
        self.PortAllocator.resetPorts()
        self.MainThreadManager = MainThreadManager(
            self.denoiseSet,
            self.disableSaveFullFiles,
            self.root,
            self.major_version,
            self.minor_version,
            self.GlobalFileManager,
            self.readerPlotFrame,
            self.SummaryFigureCanvas,
            self.resetRun,
            self.guidedSetupForm,
        )
        self.Buttons.MainThreadManager = self.MainThreadManager

    def displayReaderRunResults(self):
        if self.MainThreadManager.finishedEquilibrationPeriod:
            endOfExperimentView = EndOfExperimentView(self.root, self.GlobalFileManager)
            endOfExperimentFrame = endOfExperimentView.createEndOfExperimentView()
            self.Buttons.createGuidedSetupButton(endOfExperimentFrame)
            self.Buttons.GuidedSetupButton.place()
            self.SummaryFigureCanvas.frequencyCanvas = None
            self.endOfExperimentFrame = endOfExperimentFrame
        else:
            self.Buttons.createGuidedSetupButton(self.readerPlotFrame)
            self.Buttons.GuidedSetupButton.invokeButton()
