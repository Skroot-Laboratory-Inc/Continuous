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

    def freqToggleSetting(self, toggle):
        self.AppModule.MainThreadManager.freqToggleSet.on_next(toggle)
        logging.info(f'freqToggleSet changed to {toggle}')

    def createReaders(self, numReaders, SibInterfaces):
        self.AppModule.ColorCycler.reset()
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
                        self.AppModule.MainThreadManager.freqToggleSet
                    ))
            self.ReaderPageManager.createNextAndPreviousFrameButtons()
            self.ReaderPageManager.showPage(self.ReaderPageManager.getPage(0))
            self.updateFontSize()

    def updateFontSize(self):
        numberReaders = len(self.AppModule.Readers)
        if numberReaders > 1:
            fontsize = 9
        else:
            fontsize = 13
        mpl.rcParams.update({'font.size': fontsize})
