import tkinter as tk

from src.app.ui_manager.theme.colors import Colors
from src.app.ui_manager.theme.gui_properties import GuiProperties
from src.app.widget.progress_bar import TimedProgressBar


class ProgressBarBackground:
    def __init__(self, parent, subscriptionSubject):

        self.backgroundFrame: tk.Frame = tk.Frame(parent, bg=Colors().body.background)
        self.GuiProperties = GuiProperties()
        self.progressbar, self.popupBodyFrame = self.createBodyFrame()
        subscriptionSubject.subscribe(lambda toggle: self.toggleProgressBar(toggle))

    def createBodyFrame(self):
        bodyFrame = tk.Frame(self.backgroundFrame, bg=Colors().body.background)
        bodyFrame.place(relx=0, rely=0, relwidth=1, relheight=1)
        progressBar = TimedProgressBar(bodyFrame)
        return progressBar, bodyFrame

    def toggleProgressBar(self, showPopup):
        if showPopup:
            self.backgroundFrame.place(
                relx=0,
                rely=0,
                relheight=1,
                relwidth=1)
            self.backgroundFrame.tkraise()
        else:
            self.backgroundFrame.place_forget()
