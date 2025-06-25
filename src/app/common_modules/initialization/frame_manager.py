from src.app.ui_manager.theme.gui_properties import GuiProperties
from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.root_manager import RootManager


class FrameManager:
    def __init__(self, rootManager: RootManager):
        self.Colors = Colors()
        self.RootManager = rootManager
        self.GuiProperties = GuiProperties()
        self.bannerFrame = self.createBannerFrame()
        self.bodyFrame = self.createBodyFrame()
        self.footerFrame = self.createFooterFrame()

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
                        relheight=self.GuiProperties.bodyHeight)
        return bodyFrame

    def createFooterFrame(self):
        footerFrame = self.RootManager.createFrame(self.Colors.secondaryColor)
        footerFrame.place(
            relx=0,
            rely=1 - self.GuiProperties.footerHeight,
            relwidth=1,
            relheight=self.GuiProperties.footerHeight)
        return footerFrame
