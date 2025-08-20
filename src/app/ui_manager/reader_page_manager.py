import tkinter as tk

from reactivex import operators
from reactivex.subject import BehaviorSubject

from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.gui_properties import GuiProperties


class ReaderPageManager:
    def __init__(self, bodyFrame: tk.Frame, rootManager: RootManager):
        self.readerPages = []
        self.bodyFrame = bodyFrame
        self.Colors = Colors()
        self.GuiProperties = GuiProperties()
        self.rootManager = rootManager
        self.currentFrame = BehaviorSubject(None)

    def createPages(self, numScreens):
        for i in range(numScreens):
            readerPage = tk.Frame(self.bodyFrame, bg=self.Colors.secondaryColor)
            readerPage.grid_rowconfigure(0, weight=1)
            readerPage.grid_columnconfigure(0, weight=0)
            readerPage.grid_columnconfigure(1, weight=1)
            readerPage.grid_columnconfigure(2, weight=0)
            self.readerPages.append(readerPage)
        self.currentFrame.pipe(
            operators.pairwise()
        ).subscribe(lambda frames: self.showPage(frames[0], frames[1]))

    def showPage(self, previousFrame: tk.Frame, currentFrame: tk.Frame):
        currentFrame.place(relx=0, rely=0, relwidth=1, relheight=1)
        if currentFrame != previousFrame and previousFrame:
            previousFrame.place_forget()

    def getPage(self, screenNumber):
        return self.readerPages[screenNumber]

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

    def createReaderPageToggle(self, previousPage, currentPage, nextPage):
        previousButton = GenericButton(
            "⟨",
            currentPage,
            lambda: self.currentFrame.on_next(previousPage),
            "Toggle.TButton").button
        previousButton.grid(row=0, column=0, sticky='nsew')
        nextButton = GenericButton(
            "⟩",
            currentPage,
            lambda: self.currentFrame.on_next(nextPage),
            "Toggle.TButton").button
        nextButton.grid(row=0, column=2, sticky='nsew')
