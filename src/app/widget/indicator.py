from src.app.ui_manager.theme.colors import Colors


class Indicator:
    def __init__(self, readerNumber, readerPage):
        self.indicatorColor = Colors().status.success
        self.readerPage = readerPage
        self.readerNumber = readerNumber
        self.indicatorCanvas, self.indicator = self.readerPage.getIndicator()

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
