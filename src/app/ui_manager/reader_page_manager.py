import logging
import tkinter as tk

from reactivex import operators
from reactivex.subject import BehaviorSubject

from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.common_modules.thread_manager.reader_page_thread_manager import ReaderPageThreadManager
from src.app.use_case.use_case_factory import ContextFactory
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
        logging.info(f"appendReader called, readerPage={readerPage}, last_page={self.readerPages[-1] if self.readerPages else None}", extra={"id": "ReaderPageManager"})
        if not readerPage or readerPage == self.readerPages[-1]:
            logging.info("Creating new reader page and ReaderPageThreadManager", extra={"id": "ReaderPageManager"})
            readerPage = tk.Frame(self.bodyPage, bg=Colors().body.background)
            self.readerPages.append(readerPage)
            logging.info(f"Creating ReaderPageThreadManager for page {len(self.readerPages)}", extra={"id": "ReaderPageManager"})
            ReaderPageThreadManager(
                readerPage,
                len(self.readerPages),
                self.rootManager,
                self.sessionManager,
                self.SibFinder,
                self.appendReader,
            )
            logging.info("ReaderPageThreadManager created", extra={"id": "ReaderPageManager"})
            if self.currentFrame.value:
                logging.info("Triggering currentFrame.on_next", extra={"id": "ReaderPageManager"})
                self.currentFrame.on_next(self.currentFrame.value)
                logging.info("currentFrame.on_next completed", extra={"id": "ReaderPageManager"})
        else:
            logging.info("Not creating new page (condition not met)", extra={"id": "ReaderPageManager"})
        logging.info("appendReader completed", extra={"id": "ReaderPageManager"})

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
    nextButton = GenericButton(
        "⟩",
        parent,
        lambda: nextPageFunc,
        "Toggle.TButton").button
    if ContextFactory().showNextPageToggle():
        previousButton.grid(row=0, column=0, sticky='nsew')
        nextButton.grid(row=0, column=2, sticky='nsew')
    return previousButton, nextButton


def createBodyPage(bodyFrame):
    bodyFrame.grid_columnconfigure(0, weight=0)
    bodyFrame.grid_columnconfigure(1, weight=1)
    bodyFrame.grid_columnconfigure(2, weight=0)
    bodyFrame.grid_rowconfigure(0, weight=1)
    bodyPage = tk.Frame(bodyFrame, bg=Colors().body.background)
    bodyPage.grid(row=0, column=1, sticky="nsew")
    return bodyPage
