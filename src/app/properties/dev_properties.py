import os

from src.app.helper_methods.file_manager.common_file_manager import CommonFileManager


class DevProperties:
    def __init__(self):
        self.devBaseFolder = CommonFileManager().getDevBaseFolder()
        self.tryDevMode = True
        self.authEnabled = True
        self.disableAws = True
        self.enforceScanRate = True
        self.sibShouldError = False
        self.useMockSecondaryAxis = True
        self.errorScans = range(5, 200)
        self.devScanTime = 5
        if os.path.exists(self.devBaseFolder) and self.tryDevMode:
            self.isDevMode = True
        else:
            self.isDevMode = False
        self.startTime = 0*60  # Minutes
        self.scanRate = 0.1/60
        self.mode = "GUI"
        # self.mode = "Analysis"
