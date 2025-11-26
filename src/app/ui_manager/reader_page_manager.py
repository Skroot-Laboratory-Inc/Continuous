import tkinter as tk

from reactivex import operators
from reactivex.subject import BehaviorSubject

from src.app.authentication.session_manager.session_manager import SessionManager
from src.app.common_modules.thread_manager.reader_page_thread_manager import ReaderPageThreadManager
from src.app.reader.sib.sib_finder import SibFinder
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.gui_properties import GuiProperties


class ReaderPageManager:
    def __init__(self, bodyFrame: tk.Frame, rootManager: RootManager, sessionManager: SessionManager):
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.readerPages = []

        self.SibFinder = SibFinder()
        self.GuiProperties = GuiProperties()
        self.bodyPage = createBodyPage(bodyFrame)
        self.currentFrame = BehaviorSubject(None)
        self.previousButton, self.nextButton = createReaderPageToggle(
            bodyFrame,
            None,
            None
        )

    def appendReader(self, readerPage: tk.Frame = None):
        if not readerPage or readerPage == self.readerPages[-1]:
            readerPage = tk.Frame(self.bodyPage, bg=Colors().body.background)
            self.readerPages.append(readerPage)
            ReaderPageThreadManager(
                readerPage,
                len(self.readerPages),
                self.rootManager,
                self.sessionManager,
                self.SibFinder,
                self.appendReader,
            )
            if self.currentFrame.value:
                self.currentFrame.on_next(self.currentFrame.value)

    def createPages(self):
        self.currentFrame.pipe(
            operators.pairwise()
        ).subscribe(lambda frames: self.showPage(frames[0], frames[1]))
        self.appendReader()
        self.currentFrame.on_next(self.readerPages[0])

    def showPage(self, previousFrame: tk.Frame, currentFrame: tk.Frame):
        currentFrame.place(relx=0, rely=0, relwidth=1, relheight=1)
        currentFrameIndex = self.readerPages.index(currentFrame)

        previousIndex = (currentFrameIndex - 1) % len(self.readerPages)
        nextIndex = (currentFrameIndex + 1) % len(self.readerPages)
        self.previousButton.configure(command=lambda: self.currentFrame.on_next(self.readerPages[previousIndex]))
        self.nextButton.configure(command=lambda: self.currentFrame.on_next(self.readerPages[nextIndex]))

        if currentFrame != previousFrame and previousFrame:
            previousFrame.place_forget()


def createReaderPageToggle(parent, previousPageFunc, nextPageFunc):
    previousButton = GenericButton(
        "⟨",
        parent,
        lambda: previousPageFunc,
        "Toggle.TButton").button
    # previousButton.grid(row=0, column=0, sticky='nsew')
    nextButton = GenericButton(
        "⟩",
        parent,
        lambda: nextPageFunc,
        "Toggle.TButton").button
    # nextButton.grid(row=0, column=2, sticky='nsew')
    return previousButton, nextButton


def createBodyPage(bodyFrame):
    bodyFrame.grid_columnconfigure(0, weight=0)
    bodyFrame.grid_columnconfigure(1, weight=1)
    bodyFrame.grid_columnconfigure(2, weight=0)
    bodyFrame.grid_rowconfigure(0, weight=1)
    bodyPage = tk.Frame(bodyFrame, bg=Colors().body.background)
    bodyPage.grid(row=0, column=1, sticky="nsew")
    return bodyPage
