import glob
import os
import subprocess as sp

import logger
from dev import DevMode


class ServerFileShare:
    def __init__(self, AppModule):
        self.AppModule = AppModule
        self.DevMode = DevMode()
        self.disabled = False
        self.setServerLocation()

    def setServerLocation(self):
        try:
            hostname = sp.getoutput(['hostname'])
            self.serverLocationBase = ''
            if os.path.exists(rf"\\server\data") == True:
                self.serverLocationBase = rf"\\server\data\{hostname}"
                if os.path.exists(self.serverLocationBase) == False:
                    os.mkdir(self.serverLocationBase)
            elif os.path.exists(
                    'C:\\Users\\CameronGreenwalt\\Desktop\\Calibration\\fakeServer') == True and self.DevMode.fakeServer == True:
                self.serverLocationBase = 'C:\\Users\\CameronGreenwalt\\Desktop\\Calibration\\fakeServer\\Laptop'
                if os.path.exists(self.serverLocationBase) == False:
                    os.mkdir(self.serverLocationBase)
            if self.serverLocationBase == '':
                self.disabled = True
        except Exception as e:
            self.disabled = True
            logger.exception('Failed to find server')

    def makeNextFolder(self, folderName):
        try:
            folderNumbers = [int(os.path.basename(folder).split('_')[0]) for folder in
                             glob.glob(f'{self.serverLocationBase}\*') if
                             os.path.basename(folder).split('_')[0].isdigit()]
            if folderNumbers != []:
                folderUsed = int(max(folderNumbers)) + 1
            else:
                folderUsed = 1
            self.serverLocation = f'{self.serverLocationBase}/{folderUsed}_{folderName}'
            os.mkdir(self.serverLocation)
        except:
            logger.exception('Failed to create folder on server')
