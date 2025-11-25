from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.reader_page_allocator import ReaderPageAllocator


class Indicator:
    def __init__(self, readerNumber, readerPageAllocator: ReaderPageAllocator):

        self.indicatorColor = Colors().status.success
        self.ReaderPageAllocator = readerPageAllocator
        self.readerNumber = readerNumber
        self.indicatorCanvas, self.indicator = self.ReaderPageAllocator.getIndicator()

    def changeIndicatorGreen(self):
        self.indicatorCanvas.itemconfig(self.indicator, fill=Colors().status.success)
        self.updateHarvestJson(Colors().status.success)

    def changeIndicatorYellow(self):
        self.indicatorCanvas.itemconfig(self.indicator, fill=Colors().status.warning)
        self.updateHarvestJson(Colors().status.warning)

    def changeIndicatorRed(self):
        self.indicatorCanvas.itemconfig(self.indicator, fill=Colors().status.error)
        self.updateHarvestJson(Colors().status.error)

    def updateHarvestJson(self, harvestColor):
        self.indicatorColor = harvestColor
