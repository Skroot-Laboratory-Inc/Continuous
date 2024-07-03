import os


class DevProperties:
    def __init__(self):
        self.devBaseFolder = r'C:\\Users\\CameronGreenwalt\\Desktop\\Calibration\\dev'
        self.tryDevMode = False
        if os.path.exists(self.devBaseFolder) and self.tryDevMode:
            self.isDevMode = True
        else:
            self.isDevMode = False
        self.startTime = 0
        self.scanRate = 0.2
        # self.mode = "GUI"
        self.mode = "Analysis"