class GuiProperties:
    def __init__(self):
        """
        Main GUI configuration
        """
        self.bannerRelY = 0
        self.bannerHeight = 0.15

        self.footerHeight = 0.02

        self.bodyRelY = self.bannerHeight
        self.bodyHeight = 1 - self.bannerHeight - self.footerHeight

        self.nextPrevButtonHeight = self.bodyHeight*0.05
        self.readerPlotHeight = self.bodyHeight*0.95

        self.footerRelY = 1-self.footerHeight

        """
        Reader Page GUI configuration
        """
        self.readersPerScreen = 1
        self.numScreens = 4
