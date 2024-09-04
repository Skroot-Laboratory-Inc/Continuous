import os.path

from src.app.helper.helper_functions import getCwd, getDesktopLocation


class CommonFileManager:
    def __init__(self):
        srcDir = f"{os.path.dirname(os.path.dirname(getCwd()))}"
        resourcesDir = f"{srcDir}/src/resources"
        self.helpIconPng = rf"{resourcesDir}/help.png"
        self.addIcon = rf"{resourcesDir}/plus.png"
        self.refreshIcon = rf"{resourcesDir}/refresh.jpg"
        self.downloadPng = rf"{resourcesDir}/download.png"
        self.squareLogo = rf"{resourcesDir}/squareLogo.PNG"
        self.localDesktopFile = rf'{resourcesDir}/desktopApp.desktop'
        self.experimentLog = f'{getDesktopLocation()}/Backend/log.txt'
        self.remoteDesktopFile = rf'{os.path.dirname(srcDir)}/share/applications/desktopApp.desktop'
        self.installScript = rf'{resourcesDir}/scripts/install-script.sh'
        self.tempSoftwareUpdate = fr'{os.path.dirname(srcDir)}/DesktopApp.zip'
        self.softwareUpdatePath = fr'{os.path.dirname(srcDir)}/DesktopApp'
        self.readMe = f'{resourcesDir}/README_Analysis.md'
        self.dataSavePath = f'{getDesktopLocation()}/Experiment Data'
        self.devBaseFolder = f'{getDesktopLocation()}/Backend/dev'

    def getHelpIcon(self):
        return self.helpIconPng

    def getDownloadIcon(self):
        return self.downloadPng

    def getAddIcon(self):
        return self.addIcon

    def getRefreshIcon(self):
        return self.refreshIcon

    def getLocalDesktopFile(self):
        return self.localDesktopFile

    def getInstallScript(self):
        return self.installScript

    def getRemoteDesktopFile(self):
        return self.remoteDesktopFile

    def getTempUpdateFile(self):
        return self.tempSoftwareUpdate

    def getSoftwareUpdatePath(self):
        return self.softwareUpdatePath

    def getReadme(self):
        return self.readMe

    def getExperimentLog(self):
        return self.experimentLog

    def getDataSavePath(self):
        return self.dataSavePath

    def getSquareLogo(self):
        return self.squareLogo

    def getDevBaseFolder(self):
        return self.devBaseFolder

