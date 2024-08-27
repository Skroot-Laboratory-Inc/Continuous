from tkinter import ttk
import tkinter as tk

from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors
from src.app.ui_manager.frame_manager import FrameManager
from src.app.ui_manager.root_manager import RootManager


class ReaderPageManager:
    def __init__(self, rootManager: RootManager, showFrameFunc):
        self.readerPages = []
        self.RootManager = rootManager
        self.FrameManager = FrameManager(self.RootManager)
        self.showFrameFunc = showFrameFunc
        self.Colors = Colors()
        self.GuiProperties = GuiProperties()

    def createPages(self, numScreens):
        for i in range(numScreens):
            self.readerPages.append(self.RootManager.createFrame(self.Colors.secondaryColor))

    def showPage(self, screenNumber):
        self.showFrameFunc(
            self.readerPages[screenNumber],
            self.GuiProperties.readerPlotRelY,
            self.GuiProperties.readerPlotHeight)

    def getPage(self, screenNumber):
        return self.readerPages[screenNumber]

    def resetPages(self):
        for readerPage in self.readerPages:
            for widgets in readerPage.winfo_children():
                widgets.destroy()
        self.readerPages = []

    def createNextAndPreviousFrameButtons(self):
        for screenNumber in range(len(self.readerPages)):
            if (screenNumber + 1) != len(self.readerPages):
                self.createReaderPageToggle(
                    self.readerPages[screenNumber - 1],
                    self.readerPages[screenNumber],
                    self.readerPages[screenNumber + 1]
                )
            else:
                self.createReaderPageToggle(
                    self.readerPages[screenNumber - 1],
                    self.readerPages[screenNumber],
                    self.readerPages[0]
                )

    def createReaderPageToggle(self, previous, current, next):
        nextReaders = tk.Canvas(
            current,
            bg='gray93', highlightthickness=1, highlightbackground='black')
        nextReaders.place(relx=0.85, rely=0.96, relwidth=0.15, relheight=0.04)
        nextReaders.bind("<Button>", lambda event, frame=next: self.showPage(frame))
        nextText = ttk.Label(
            nextReaders,
            text="Next", font=("Arial", 12),
            background='gray93', borderwidth=0)
        nextText.place(anchor='center', relx=.5, rely=0.5)
        nextReaders.bind("<Button>", lambda event, frame=next: self.showPage(frame))

        previousReaders = tk.Canvas(
            current,
            bg='gray93', highlightthickness=1, highlightbackground='black')
        previousReaders.place(relx=0, rely=0.96, relwidth=0.15, relheight=0.04)
        previousReaders.bind("<Button>", lambda event, frame=previous: self.showPage(frame))
        previousText = ttk.Label(
            previousReaders,
            text="Previous", font=("Arial", 12),
            background='gray93', borderwidth=0)
        previousText.place(anchor='center', relx=0.5, rely=0.5)
        previousReaders.bind("<Button>", lambda event, frame=previous: self.showPage(frame))
