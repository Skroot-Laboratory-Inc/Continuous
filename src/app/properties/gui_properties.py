class GuiProperties:
    def __init__(self):
        """
        Main GUI configuration
        """
        self.bannerRelY = 0
        self.bannerHeight = 0.025

        self.footerHeight = 0.03

        self.bodyRelY = self.bannerHeight
        self.bodyHeight = 1 - self.bannerHeight - self.footerHeight

        self.extraWidgetsHeight = 0.05
        self.readerPlotRelY = self.bannerHeight+self.extraWidgetsHeight
        readerPlotFrameHeight = self.bodyHeight - self.extraWidgetsHeight
        self.nextPrevButtonHeight = readerPlotFrameHeight*0.05
        self.readerPlotHeight = readerPlotFrameHeight*0.95

        self.footerRelY = 1-self.footerHeight


        """
        Reader Page GUI configuration
        """
        self.maxReadersPerScreen = 4
