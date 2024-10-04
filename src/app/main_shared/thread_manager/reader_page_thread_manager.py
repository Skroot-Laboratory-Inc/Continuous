import logging
from tkinter import messagebox

from reactivex.subject import BehaviorSubject

from src.app.exception.common_exceptions import UserExitedException
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.model.guided_setup_input import GuidedSetupInput
from src.app.reader.interval_thread.reader_thread_manager import ReaderThreadManager
from src.app.reader.reader import Reader
from src.app.reader.sib.sib_finder import SibFinder
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.ui_manager.reader_page_allocator import ReaderPageAllocator
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification
from src.app.widget.guided_setup import SetupForm


class ReaderPageThreadManager:
    def __init__(self, readerPage, startingReaderNumber, finalReaderNumber, mainFreqToggleSet, rootManager: RootManager):
        self.readerAllocator = ReaderPageAllocator(
            readerPage,
            startingReaderNumber,
            finalReaderNumber,
            self.connectReader,
            self.calibrateReader,
            self.startReaderThread,
            self.stopReaderThread,
        )
        self.readerThreads = {}
        self.Readers = {}
        self.mainFreqToggleSet = mainFreqToggleSet
        self.mainFreqToggleSet.subscribe(lambda toggle: self.toggleReaderView(toggle))
        self.RootManager = rootManager
        self.SibFinder = SibFinder(rootManager)

    def toggleReaderView(self, toggle):
        for Reader in self.Readers.values():
            if Reader.finishedEquilibrationPeriod:
                Reader.currentFrequencyToggle = toggle
                # Changes to the UI need to be done in the UI thread, where the button was placed, otherwise weird issues occur.
                Reader.plotFrequencyButton.invoke()

    def connectReader(self, readerNumber):
        try:
            guidedSetupForm, globalFileManager = self.readerForm()
            shouldCalibrate = guidedSetupForm.getCalibrate()
            sib = self.SibFinder.connectSib(readerNumber, globalFileManager, shouldCalibrate)
            self.Readers[readerNumber] = Reader(
                globalFileManager,
                readerNumber,
                self.readerAllocator,
                sib,
            )
            self.readerThreads[readerNumber] = ReaderThreadManager(
                self.Readers[readerNumber],
                self.RootManager,
                guidedSetupForm,
                self.mainFreqToggleSet,
                self.resetReader,
                self.issueOccurred,
            )
            return shouldCalibrate
        except UserExitedException:
            return None
        except:
            logging.exception("Failed to connect new reader. ")
            text_notification.setText(f"Failed to connect reader for vessel {readerNumber}")
            return None

    def issueOccurred(self):
        # Will not work when more than one reader page is present.
        for readerThread in self.readerThreads.values():
            if readerThread.currentIssues != {}:
                return True
        return False

    def calibrateReader(self, readerNumber):
        self.Readers[readerNumber].SibInterface.calibrateIfRequired()
        text_notification.setText(f"Calibration Complete for Vessel {readerNumber}")

    def startReaderThread(self, readerNumber):
        self.readerThreads[readerNumber].startReaderLoop()

    def getReader(self, readerNumber) -> Reader:
        return self.Readers[readerNumber]

    def getReaderPageFrame(self, readerNumber) -> ReaderFrame:
        return self.readerAllocator.readerFrames[readerNumber]

    def resetReader(self, readerNumber):
        self.getReader(readerNumber).SibInterface.close()
        self.getReader(readerNumber).Indicator.changeIndicatorGreen()
        for widgets in self.getReaderPageFrame(readerNumber).plotFrame.winfo_children():
            widgets.destroy()

    def stopReaderThread(self, readerNumber):
        endExperiment = messagebox.askquestion(
            f'Stop Vessel #{readerNumber}',
            f'Are you sure you wish to stop vessel {readerNumber}?')
        if endExperiment == 'yes':
            logging.info('Experiment ended by user.')
            self.readerThreads[readerNumber].thread.shutdown_flag.set()
            return True
        else:
            return False

    def readerForm(self) -> (GuidedSetupInput, GlobalFileManager):
        setupForm = SetupForm(self.RootManager, GuidedSetupInput())
        try:
            return setupForm.getConfiguration()
        except:
            raise UserExitedException("The user cancelled guided setup.")
