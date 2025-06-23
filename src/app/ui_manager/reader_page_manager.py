import logging
import tkinter as tk

from src.app.properties.gui_properties import GuiProperties
from src.app.ui_manager.theme.colors import Colors


class ReaderPageManager:
    def __init__(self, bodyFrame: tk.Frame):
        self.readerPages = []
        self.bodyFrame = bodyFrame
        self.Colors = Colors()
        self.GuiProperties = GuiProperties()

    def createPages(self, numScreens):
        for i in range(numScreens):
            readerPage = tk.Frame(self.bodyFrame, bg=self.Colors.secondaryColor)
            self.readerPages.append(readerPage)

    def showPage(self, frame):
        try:
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            frame.tkraise()
        except:
            logging.exception(f'Failed to update reader screen.', extra={"id": "readerPageManager"})

    def getPage(self, screenNumber):
        return self.readerPages[screenNumber]
