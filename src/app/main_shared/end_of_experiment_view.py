import os
import threading
import tkinter as tk

from PIL import ImageTk, Image

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.helper import helper_functions
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.frame_manager import FrameManager
from src.app.ui_manager.root_manager import RootManager
from src.app.theme.colors import Colors
from src.app.widget.link_button import Linkbutton


class EndOfExperimentView:
    def __init__(self, rootManager: RootManager, globalFileManager):
        self.RootManager = rootManager
        self.GlobalFileManager = globalFileManager
        self.Colors = Colors()
        self.CommonFileManager = CommonFileManager()
        image = Image.open(self.CommonFileManager.getDownloadIcon())
        resizedImage = image.resize((15, 15), Image.LANCZOS)
        self.downloadIcon = ImageTk.PhotoImage(resizedImage)
        self.FrameManager = FrameManager(self.RootManager)

    def createEndOfExperimentView(self):
        endOfExperimentFrame = self.FrameManager.createEndOfExperimentFrame()

        fileExplorerFrame = tk.Frame(endOfExperimentFrame, bg=self.Colors.secondaryColor)
        fileExplorerFrame.grid(row=0, column=0, columnspan=3)
        fileExplorerLabel = tk.Label(fileExplorerFrame, text='Experiment File Location: ', bg='white')
        fileExplorerLabel.pack(side=tk.LEFT)
        fileExplorerButton = Linkbutton(
            fileExplorerFrame,
            font=FontTheme().primary,
            text=self.GlobalFileManager.getSavePath(),
            command=lambda: helper_functions.openFileExplorer(self.GlobalFileManager.getSavePath()))
        fileExplorerButton.pack(side=tk.LEFT)
        downloadButton = tk.Button(
            fileExplorerFrame,
            bg=self.Colors.secondaryColor,
            highlightthickness=0,
            borderwidth=0,
            image=self.downloadIcon,
            command=lambda: self.downloadExperimentAsZip())
        downloadButton.pack(side=tk.LEFT, padx=10)

        self.guidedSetupImage = ImageTk.PhotoImage(file=self.GlobalFileManager.getSetupForm())
        image_label = tk.Label(
            endOfExperimentFrame,
            image=self.guidedSetupImage,
            bg=self.Colors.secondaryColor)
        image_label.grid(row=1, column=0, sticky='nsew')

        image = Image.open(self.GlobalFileManager.getSummaryFigure()).resize((600, 400), Image.LANCZOS)
        self.summaryPlotImage = ImageTk.PhotoImage(image)
        image_label = tk.Label(endOfExperimentFrame, image=self.summaryPlotImage, bg=self.Colors.secondaryColor)
        image_label.grid(row=1, column=1, sticky='nsew')

        return endOfExperimentFrame

    def downloadExperimentAsZip(self):
        downloadThread = threading.Thread(
            target=helper_functions.downloadAsZip,
            args=(f"{self.GlobalFileManager.getSavePath()}/Analysis",
                  f"{os.path.basename(self.GlobalFileManager.getSavePath())}.zip"),
            daemon=True)
        downloadThread.start()
