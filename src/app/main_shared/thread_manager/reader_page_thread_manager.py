from src.app.ui_manager.reader_page_allocator import ReaderPageAllocator


class ReaderPageThreadManager:
    def __init__(self, readerPage, startingReaderNumber, finalReaderNumber):
        self.readerAllocator = ReaderPageAllocator(readerPage, startingReaderNumber, finalReaderNumber)

    def createThreads(self):
        pass

    def createReaders(self):
        pass

    def connectReader(self):
        pass

    def calibrateReader(self):
        pass

    def startReader(self):
        pass
