import glob
import os
import subprocess as sp

import logger


class ServerFileShare:
    def __init__(self, AppModule):
        self.serverLocationBase = ''
        self.AppModule = AppModule
        self.DevMode = AppModule.DevMode
        self.disabled = False
        if self.AppModule.os == "windows":
            self.setServerLocation()

    def setServerLocation(self):
        try:
            hostname = sp.getoutput(['hostname'])
            if os.path.exists(rf"\\server\data"):
                self.serverLocationBase = rf"\\server\data\{hostname}"
                if not os.path.exists(self.serverLocationBase):
                    os.mkdir(self.serverLocationBase)
            elif os.path.exists('C:\\Users\\CameronGreenwalt\\Desktop\\Calibration\\fakeServer') \
                    and self.DevMode.fakeServer:
                self.serverLocationBase = 'C:\\Users\\CameronGreenwalt\\Desktop\\Calibration\\fakeServer\\Laptop'
                if not os.path.exists(self.serverLocationBase):
                    os.mkdir(self.serverLocationBase)
            if self.serverLocationBase == '':
                self.disabled = True
        except:
            self.disabled = True
            logger.exception('Failed to find server')

    def makeNextFolder(self, folderName):
        try:
            folderNumbers = [int(os.path.basename(folder).split('_')[0]) for folder in
                             glob.glob(f'{self.serverLocationBase}\*') if
                             os.path.basename(folder).split('_')[0].isdigit()]
            if folderNumbers:
                folderUsed = int(max(folderNumbers)) + 1
            else:
                folderUsed = 1
            self.serverLocation = f'{self.serverLocationBase}/{folderUsed}_{folderName}'
            os.mkdir(self.serverLocation)
        except:
            logger.exception('Failed to create folder on server')
