import logging
import math
import tkinter as tk
from tkinter import messagebox, simpledialog

import matplotlib as mpl

from src.app.properties.gui_properties import GuiProperties
from src.app.reader.reader import Reader
from src.app.theme.colors import Colors
from src.app.ui_manager.frame_manager import FrameManager
from src.app.ui_manager.reader_page_allocator import ReaderPageAllocator
from src.app.ui_manager.reader_page_manager import ReaderPageManager
from src.app.ui_manager.root_manager import RootManager


class Settings:
    def __init__(self, AppModule, rootManager: RootManager):
        self.AppModule = AppModule
        self.RootManager = rootManager
        self.FrameManager = FrameManager(self.RootManager)
        self.Colors = Colors()
        self.ReaderPageManager = ReaderPageManager(self.RootManager)
        self.maxReadersPerScreen = GuiProperties().maxReadersPerScreen

    def freqRangeSetting(self):
        startFreq = simpledialog.askfloat(
            "Input", "Start Frequency (MHz): \nRange: (50-170MHz)",
            parent=self.RootManager.getRoot(),
            minvalue=50,
            maxvalue=170)
        stopFreq = simpledialog.askfloat(
            "Input",
            "Stop Frequency (MHz): \nRange: (50-170MHz)",
            parent=self.RootManager.getRoot(),
            minvalue=50,
            maxvalue=170)
        if startFreq is not None:
            for Reader in self.AppModule.Readers:
                Reader.SibInterface.setStartFrequency(startFreq)
            self.AppModule.startFreq = startFreq
            logging.info(f'startFreq changed to {startFreq}')
        if stopFreq is not None:
            for Reader in self.AppModule.Readers:
                Reader.SibInterface.setStopFrequency(stopFreq)
            self.AppModule.stopFreq = stopFreq
            logging.info(f'stopFreq changed to {stopFreq}')

    def saveFilesSetting(self):
        disableSaveFullFiles = messagebox.askyesno(
            "Disable Full File Save",
            "Are you sure you would like to disable entire file save? \n",
            parent=self.RootManager.getRoot())
        if disableSaveFullFiles is not None:
            self.AppModule.disableSaveFullFiles = disableSaveFullFiles
            logging.info(f'disableSaveFullFiles changed to {disableSaveFullFiles}')

    def rateSetting(self):
        scanRate = simpledialog.askfloat(
            "Input",
            "Scan Rate (minutes between scans): \nRange: (0.1 - 240)",
            parent=self.RootManager.getRoot(),
            minvalue=0.1,
            maxvalue=240)
        if scanRate is not None:
            self.AppModule.guidedSetupForm.scanRate = scanRate
            self.AppModule.MainThreadManager.scanRate = scanRate
            logging.info(f'scanRate changed to {scanRate}')

    def denoiseSetting(self):
        self.AppModule.denoiseSet = messagebox.askyesno(
            'Denoise Setting',
            'Would you like to denoise and smooth the results before displaying them?')
        logging.info(f'denoiseSet changed to {self.AppModule.denoiseSet}')

    def freqToggleSetting(self, toggle):
        self.AppModule.MainThreadManager.freqToggleSet.on_next(toggle)
        logging.info(f'freqToggleSet changed to {toggle}')

    def weakSignalToggleSetting(self):
        self.AppModule.weakSignalToggleSet = messagebox.askyesno(
            'Ignore Weak Signal',
            'Are you sure you would like to ignore the weak signal warning?')
        logging.info(f'weakSignalToggleSet changed to {self.AppModule.denoiseSet}')

    def createReaders(self, numReaders, SibInterfaces):
        self.AppModule.ColorCycler.reset()
        self.addReaderNotes()
        if self.AppModule.guidedSetupForm.getSecondAxisTitle() != "":
            self.addReaderSecondAxis()
        self.addInoculation()
        if numReaders is not None:
            numScreens = math.ceil(numReaders / self.maxReadersPerScreen)
            self.ReaderPageManager.createPages(numScreens)
            for screenNumber in range(0, numScreens):
                readerPage = self.ReaderPageManager.getPage(screenNumber)
                isLastScreen = screenNumber == numScreens-1
                if isLastScreen and numReaders % self.maxReadersPerScreen != 0:
                    onScreenReaders = numReaders % self.maxReadersPerScreen
                else:
                    onScreenReaders = self.maxReadersPerScreen
                readerAllocator = ReaderPageAllocator(readerPage, onScreenReaders)
                startingReaderNumber = 1 + screenNumber*self.maxReadersPerScreen
                finalReaderNumber = startingReaderNumber + onScreenReaders
                for readerNumber in range(startingReaderNumber, finalReaderNumber):
                    readerColor = self.AppModule.ColorCycler.getNext()
                    self.AppModule.Readers.append(Reader(
                        self.AppModule,
                        readerNumber,
                        readerAllocator,
                        self.AppModule.startFreq,
                        self.AppModule.stopFreq,
                        self.AppModule.guidedSetupForm.getSavePath(),
                        readerColor,
                        SibInterfaces[readerNumber - 1],
                        self.AppModule.ExperimentNotes,
                        self.AppModule.MainThreadManager.freqToggleSet
                    ))
            self.ReaderPageManager.createNextAndPreviousFrameButtons()
            self.ReaderPageManager.showPage(self.ReaderPageManager.getPage(0))
            self.updateFontSize()

    def addReaderNotes(self):
        try:
            self.AppModule.menubar.delete("Experiment Notes")
        except:
            pass
        if self.AppModule.Readers:
            settingsMenuNotes = tk.Menu(self.AppModule.menubar, tearoff=0)
            settingsMenuNotes.add_command(label=f"All Readers", command=lambda: self.addNotesAllReaders())
            for Reader in self.AppModule.Readers:
                Reader.addExperimentNotesMenubar(settingsMenuNotes)
            self.AppModule.menubar.add_cascade(label="Experiment Notes", menu=settingsMenuNotes)

    def addReaderSecondAxis(self):
        try:
            self.AppModule.menubar.delete("Second Axis")
        except:
            pass
        if self.AppModule.Readers:
            settingsMenuSecondAxis = tk.Menu(self.AppModule.menubar, tearoff=0)
            for Reader in self.AppModule.Readers:
                Reader.addSecondAxisMenubar(settingsMenuSecondAxis)
            self.AppModule.menubar.add_cascade(label="Second Axis", menu=settingsMenuSecondAxis)

    def addInoculation(self):
        try:
            self.AppModule.menubar.delete("Inoculation")
        except:
            pass
        settingsMenuNotes = tk.Menu(self.AppModule.menubar, tearoff=0)
        settingsMenuNotes.add_command(label=f"All readers inoculated", command=lambda: self.inoculateAllReaders())
        for Reader in self.AppModule.Readers:
            Reader.addInoculationMenuBar(settingsMenuNotes)
        # self.AppModule.menubar.add_cascade(label="Inoculation", menu=settingsMenuNotes)

    def inoculateAllReaders(self):
        genericReader = self.AppModule.Readers[0]
        genericReader.HarvestAlgorithm.updateInoculationExperimentNotes(0, genericReader.getAnalyzer().ResultSet)
        for Reader in self.AppModule.Readers:
            Reader.HarvestAlgorithm.updateInoculationValues(Reader.getAnalyzer().ResultSet)
        self.AppModule.menubar.delete("Inoculation")

    def addNotesAllReaders(self):
        newNotes = simpledialog.askstring(f'All Reader Notes',
                                             f'Add any experiment notes here. \n'
                                             f'They will be applied to all readers. \n'
                                             f'They can be viewed in the pdf generated.')
        genericReader = self.AppModule.Readers[0]
        genericReader.ExperimentNotes.updateExperimentNotes(0, newNotes, genericReader.getResultSet())

    def updateFontSize(self):
        numberReaders = len(self.AppModule.Readers)
        if numberReaders > 1:
            fontsize = 9
        else:
            fontsize = 13
        mpl.rcParams.update({'font.size': fontsize})
