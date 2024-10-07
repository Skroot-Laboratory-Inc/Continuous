class GuiProperties:
    def __init__(self):
        """
        Main GUI configuration
        """
        self.bannerRelY = 0
        self.bannerHeight = 0.025

        self.footerHeight = 0.04

        self.bodyRelY = self.bannerHeight
        self.bodyHeight = 1 - self.bannerHeight - self.footerHeight

        self.nextPrevButtonHeight = self.bodyHeight*0.05
        self.readerPlotHeight = self.bodyHeight*0.95

        self.footerRelY = 1-self.footerHeight


        """
        Reader Page GUI configuration
        """
        self.readersPerScreen = 4
        self.numScreens = 1
