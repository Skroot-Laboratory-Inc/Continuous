import logging
import tkinter as tk

from reactivex import operators
from reactivex.subject import BehaviorSubject

from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.use_case.use_case_factory import ContextFactory
from src.app.reader.sib.sib_finder import SibFinder
from src.app.ui_manager.buttons.generic_button import GenericButton
from src.app.ui_manager.reader_page import ReaderPage
from src.app.ui_manager.root_manager import RootManager
from src.app.ui_manager.theme.colors import Colors


class ReaderPageManager:
    """
    Manages multiple reader pages with navigation.
    Simplified: Each page now contains exactly one reader (previously supported multiple readers per page).
    """
    def __init__(self, bodyFrame: tk.Frame, rootManager: RootManager, sessionManager: SessionManager):
        self.rootManager = rootManager
        self.sessionManager = sessionManager
        self.readerPages = []
        self.SibFinder = SibFinder()
        self.bodyPage = self._createBodyPage(bodyFrame)
        self.currentFrame = BehaviorSubject(None)
        self.previousButton, self.nextButton = self._createReaderPageToggle(bodyFrame)

    def appendReader(self, currentPageFrame: tk.Frame = None):
        """
        Append a new reader page. Each page contains exactly one reader.
        If called with the current page, creates a new page for the next reader.
        """
        if not currentPageFrame or currentPageFrame == self.readerPages[-1]:
            try:
                pageFrame = tk.Frame(self.bodyPage, bg=Colors().body.background)
                self.readerPages.append(pageFrame)
                ReaderPage(
                    pageFrame,
                    len(self.readerPages),  # Reader number
                    self.rootManager,
                    self.sessionManager,
                    self.SibFinder,
                    self.appendReader,
                )
            except:
                logging.exception("Failed to add new reader page.", extra={"id": "reader_page_manager"})

    def createPages(self):
        """Initialize the first reader page and set up navigation."""
        self.currentFrame.pipe(
            operators.pairwise()
        ).subscribe(lambda frames: self._showPage(frames[0], frames[1]))
        self.appendReader()
        self.currentFrame.on_next(self.readerPages[0])

    def _showPage(self, previousFrame: tk.Frame, currentFrame: tk.Frame):
        """Display the current page and hide the previous one."""
        currentFrame.place(relx=0, rely=0, relwidth=1, relheight=1)
        currentFrameIndex = self.readerPages.index(currentFrame)

        previousIndex = (currentFrameIndex - 1) % len(self.readerPages)
        nextIndex = (currentFrameIndex + 1) % len(self.readerPages)
        self.previousButton.configure(command=lambda: self.currentFrame.on_next(self.readerPages[previousIndex]))
        self.nextButton.configure(command=lambda: self.currentFrame.on_next(self.readerPages[nextIndex]))

        if currentFrame != previousFrame and previousFrame:
            previousFrame.place_forget()

    @staticmethod
    def _createReaderPageToggle(bodyFrame):
        """Create previous/next navigation buttons."""
        previousButton = GenericButton(
            "⟨",
            bodyFrame,
            lambda: None,  # Command set dynamically in _showPage
            "Toggle.TButton").button
        nextButton = GenericButton(
            "⟩",
            bodyFrame,
            lambda: None,  # Command set dynamically in _showPage
            "Toggle.TButton").button

        if ContextFactory().showNextPageToggle():
            previousButton.grid(row=0, column=0, sticky='nsew')
            nextButton.grid(row=0, column=2, sticky='nsew')

        return previousButton, nextButton

    @staticmethod
    def _createBodyPage(bodyFrame):
        """Create the main body page container."""
        bodyFrame.grid_columnconfigure(0, weight=0)
        bodyFrame.grid_columnconfigure(1, weight=1)
        bodyFrame.grid_columnconfigure(2, weight=0)
        bodyFrame.grid_rowconfigure(0, weight=1)
        bodyPage = tk.Frame(bodyFrame, bg=Colors().body.background)
        bodyPage.grid(row=0, column=1, sticky="nsew")
        return bodyPage
