import logging
from tkinter import messagebox

from src.app.exception.common_exceptions import UserExitedException
from src.app.reader.interval_thread.reader_thread_manager import ReaderThreadManager
from src.app.reader.reader import Reader
from src.app.reader.sib.sib_finder import SibFinder
from src.app.ui_manager.model.reader_frame import ReaderFrame
from src.app.ui_manager.reader_page_allocator import ReaderPageAllocator
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification


class ReaderPageThreadManager:
    def __init__(self, readerPage, startingReaderNumber, finalReaderNumber, mainFreqToggleSet,
                 rootManager: RootManager):
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
            guidedSetupForm, globalFileManager = self.readerAllocator.getReaderFrame(readerNumber).setupReaderForm.getConfiguration()
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
            logging.exception("Failed to connect new reader.", extra={"id": f"Reader {readerNumber}"})
            text_notification.setText(f"Failed to connect reader for vessel {readerNumber}")
            return None

    def issueOccurred(self):
        # Will not work when more than one reader page is present.
        for readerThread in self.readerThreads.values():
            if readerThread.currentIssues != {}:
                return True
        return False

    def calibrateReader(self, readerNumber):
        readerFrame = self.readerAllocator.getReaderFrame(readerNumber)
        readerFrame.calibrateButton.disable()
        text_notification.setText(f"Calibration started for Vessel {readerNumber}")
        self.Readers[readerNumber].SibInterface.calibrateIfRequired()
        text_notification.setText(f"Calibration Complete for Vessel {readerNumber}")
        readerFrame.calibrateButton.hide()
        readerFrame.startButton.enable()
        readerFrame.showPlotFrame()

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
            logging.info('Experiment ended by user.', extra={"id": f"Reader {readerNumber}"})
            readerFrame = self.readerAllocator.getReaderFrame(readerNumber)
            readerFrame.stopButton.disable()
            text_notification.setText(
                f"Stopped scanning for vessel {readerNumber}. Please wait for current sweep to complete to reset it."
            )
            self.readerThreads[readerNumber].thread.shutdown_flag.set()
            self.readerThreads[readerNumber].thread.join()
            readerFrame.hidePlotFrame()
            readerFrame.createButton.show()
            readerFrame.resetSetupForm(readerNumber)
            readerFrame.timer.resetTimer()
        else:
            return False
