from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors
from src.app.ui_manager.root_manager import RootManager


class FrameManager:
    def __init__(self, rootManager: RootManager):
        self.Colors = Colors()
        self.RootManager = rootManager
        self.GuiProperties = GuiProperties()

    def createBannerFrame(self):
        bannerFrame = self.RootManager.createFrame(self.Colors.secondaryColor)
        bannerFrame.place(relx=0,
                          rely=0,
                          relwidth=1,
                          relheight=self.GuiProperties.bannerHeight)
        return bannerFrame

    def createBodyFrame(self):
        bodyFrame = self.RootManager.createFrame(self.Colors.secondaryColor)
        bodyFrame.place(relx=0,
                        rely=self.GuiProperties.bodyRelY,
                        relwidth=1,
                        relheight=self.GuiProperties.mainHeight)
        return bodyFrame

    def createEndOfExperimentFrame(self):
        endOfExperimentFrame = self.createBodyFrame()
        endOfExperimentFrame.grid_rowconfigure(0, weight=1)
        endOfExperimentFrame.grid_rowconfigure(1, weight=10)
        endOfExperimentFrame.grid_rowconfigure(2, weight=1)
        endOfExperimentFrame.grid_columnconfigure(0, weight=2)
        endOfExperimentFrame.grid_columnconfigure(1, weight=3)
        return endOfExperimentFrame

    def createFooterFrame(self):
        footerFrame = self.RootManager.createFrame(self.Colors.secondaryColor)
        footerFrame.place(
            relx=0,
            rely=1 - self.GuiProperties.footerHeight,
            relwidth=1,
            relheight=self.GuiProperties.footerHeight)
        return footerFrame
