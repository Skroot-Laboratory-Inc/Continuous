import os

from src.app.file_manager.common_file_manager import CommonFileManager


class DevProperties:
    def __init__(self):
        self.devBaseFolder = CommonFileManager().getDevBaseFolder()
        self.tryDevMode = False
        self.disableAws = True
        if os.path.exists(self.devBaseFolder) and self.tryDevMode:
            self.isDevMode = True
        else:
            self.isDevMode = False
        self.startTime = 48*60  # Minutes
        self.scanRate = .5/60
        # self.mode = "GUI"
        self.mode = "Analysis"

