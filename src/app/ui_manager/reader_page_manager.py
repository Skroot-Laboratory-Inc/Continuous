import logging
import tkinter as tk
from tkinter import ttk

from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager


class ReaderPageManager:
    def __init__(self, rootManager: RootManager):
        self.readerPages = []
        self.RootManager = rootManager
        self.Colors = Colors()
        self.GuiProperties = GuiProperties()

    def createPages(self, numScreens):
        for i in range(numScreens):
            readerPage = self.RootManager.createFrame(self.Colors.secondaryColor)
            readerPage.grid_rowconfigure(0, weight=1, uniform="plot")
            readerPage.grid_rowconfigure(1, weight=1, uniform="plot")
            readerPage.grid_columnconfigure(0, weight=1, uniform="plot")
            readerPage.grid_columnconfigure(1, weight=1, uniform="plot")
            self.readerPages.append(readerPage)

    def showPage(self, frame):
        try:
            frame.place(relx=0,
                        rely=self.GuiProperties.bodyRelY,
                        relwidth=1,
                        relheight=self.GuiProperties.bodyHeight)
            frame.tkraise()
        except:
            logging.exception(f'Failed to update reader screen.')

    def getPage(self, screenNumber):
        return self.readerPages[screenNumber]

    def resetPages(self):
        for readerPage in self.readerPages:
            for widgets in readerPage.winfo_children():
                widgets.destroy()
        self.readerPages = []

    def createNextAndPreviousFrameButtons(self):
        if len(self.readerPages) > 1:
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
        previousReaders = tk.Canvas(
            current,
            height=30, width=150,
            bg='gray93', highlightthickness=1, highlightbackground='black')
        previousReaders.grid(row=2, column=0, sticky='w', padx=10, pady=10)
        previousReaders.bind("<Button>", lambda event, frame=previous: self.showPage(frame))
        previousText = ttk.Label(
            previousReaders,
            text="Previous", font=FontTheme().header3,
            background='gray93', borderwidth=0)
        previousText.place(anchor='center', relx=0.5, rely=0.5)
        previousReaders.bind("<Button>", lambda event, frame=previous: self.showPage(frame))

        nextReaders = tk.Canvas(
            current,
            height=30, width=150,
            bg='gray93', highlightthickness=1, highlightbackground='black')
        nextReaders.grid(row=2, column=1, sticky='e', padx=10, pady=10)
        nextReaders.bind("<Button>", lambda event, frame=next: self.showPage(frame))
        nextText = ttk.Label(
            nextReaders,
            text="Next", font=FontTheme().header3,
            background='gray93', borderwidth=0)
        nextText.place(anchor='center', relx=.5, rely=0.5)
        nextReaders.bind("<Button>", lambda event, frame=next: self.showPage(frame))
