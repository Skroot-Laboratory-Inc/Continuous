import os.path

from src.app.helper.helper_functions import getCwd, getDesktopLocation


class CommonFileManager:
    def __init__(self):
        rootDir = f"{os.path.dirname(getCwd())}"
        resourcesDir = f"{rootDir}/resources"
        self.helpIconPng = rf"{resourcesDir}/help.png"
        self.downloadPng = rf"{resourcesDir}/download.png"
        self.squareLogo = rf"{resourcesDir}/squareLogo.PNG"
        self.localDesktopFile = rf'{resourcesDir}/desktopApp.desktop'
        self.experimentLog = f'{getDesktopLocation()}/Calibration/log.txt'
        self.remoteDesktopFile = rf'{os.path.dirname(rootDir)}/share/applications/desktopApp.desktop'
        self.installScript = rf'{resourcesDir}/scripts/install-script.sh'
        self.tempSoftwareUpdate = fr'{rootDir}/DesktopApp.zip'
        self.readMe = f'{resourcesDir}/README_Analysis.md'
        self.dataSavePath = f'{getDesktopLocation()}/data'

    def getHelpIcon(self):
        return self.helpIconPng

    def getDownloadIcon(self):
        return self.downloadPng

    def getLocalDesktopFile(self):
        return self.localDesktopFile

    def getInstallScript(self):
        return self.installScript

    def getRemoteDesktopFile(self):
        return self.remoteDesktopFile

    def getTempUpdateFile(self):
        return self.tempSoftwareUpdate

    def getReadme(self):
        return self.readMe

    def getExperimentLog(self):
        return self.experimentLog

    def getDataSavePath(self):
        return self.dataSavePath

    def getSquareLogo(self):
        return self.squareLogo

