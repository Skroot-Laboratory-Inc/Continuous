import tkinter as tk

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.gui_properties import GuiProperties


class PopupBackground:
    def __init__(self, rootManager):
        self.Colors = Colors()
        self.backgroundFrame: tk.Frame = rootManager.createFrame(self.Colors.secondaryColor)
        self.RootManager = rootManager
        self.GuiProperties = GuiProperties()
        self.bodyFrame = self.createBodyFrame()
        self.RootManager.popupDisplayed.subscribe(lambda toggle: self.togglePopupBackground(toggle))

    def createBodyFrame(self):
        bodyFrame = tk.Frame(self.backgroundFrame, bg=self.Colors.secondaryColor)
        bodyFrame.place(relx=0, rely=0, relwidth=1, relheight=1)
        return bodyFrame

    def togglePopupBackground(self, showPopup):
        if showPopup:
            self.backgroundFrame.place(
                relx=0,
                rely=self.GuiProperties.bodyRelY,
                relheight=self.GuiProperties.bodyHeight,
                relwidth=1)
            self.backgroundFrame.tkraise()
        else:
            self.backgroundFrame.place_forget()