import os.path


class CommonFileManager:
    def __init__(self):
        srcDir = f"{os.path.dirname(os.path.dirname(getCwd()))}"
        resourcesDir = f"{srcDir}/src/resources"
        self.helpIconPng = rf"{resourcesDir}/media/help.png"
        self.profileIcon = rf"{resourcesDir}/media/profile.jpg"
        self.skrootLogo = rf"{resourcesDir}/media/squareLogo.PNG"
        self.addIcon = rf"{resourcesDir}/media/plus.png"
        self.powerIcon = rf"{resourcesDir}/media/power.png"
        self.localDesktopFile = rf'{resourcesDir}/ubuntu_settings/desktopApp.desktop'
        self.troubleshootingDoc = rf"{resourcesDir}/media/troubleshootingDoc.pdf"
        self.advancedSettingsDoc = rf"{resourcesDir}/media/advancedSettings.pdf"
        self.userGuideDoc = rf"{resourcesDir}/media/userGuideDoc.pdf"
        self.experimentLog = f'{getDesktopLocation()}/Backend/log.txt'
        self.remoteDesktopFile = rf'{os.path.dirname(srcDir)}/share/applications/desktopApp.desktop'
        self.updateScript = rf'{resourcesDir}/scripts/update-script.sh'
        self.tempSoftwareUpdate = fr'{os.path.dirname(srcDir)}/DesktopApp.zip'
        self.tempReleaseNotes = fr'{os.path.dirname(srcDir)}'
        self.softwareUpdatePath = fr'{os.path.dirname(srcDir)}/DesktopApp'
        self.dataSavePath = f'{getDesktopLocation()}/Experiment Data'
        self.devBaseFolder = f'{getDesktopLocation()}/Backend/dev/Benchtop'

    def getHelpIcon(self):
        return self.helpIconPng

    def getAddIcon(self):
        return self.addIcon

    def getPowerIcon(self):
        return self.powerIcon

    def getLocalDesktopFile(self):
        return self.localDesktopFile

    def getUpdateScript(self):
        return self.updateScript

    def getRemoteDesktopFile(self):
        return self.remoteDesktopFile

    def getTempUpdateFile(self):
        return self.tempSoftwareUpdate

    def getTempNotes(self):
        return self.tempReleaseNotes

    def getSoftwareUpdatePath(self):
        return self.softwareUpdatePath

    def getExperimentLog(self):
        return self.experimentLog

    def getDataSavePath(self):
        if not os.path.exists(self.dataSavePath):
            os.mkdir(self.dataSavePath)
        return self.dataSavePath

    def getDevBaseFolder(self):
        return self.devBaseFolder

    def getSkrootLogo(self):
        return self.skrootLogo

    def getProfileIcon(self):
        return self.profileIcon


def getCwd():
    """ This gets the directory the app is being run from i.e. the path to main.py. """
    return os.getcwd()


def getDesktopLocation():
    """ This gets the path to the computer's desktop. """
    try:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except KeyError:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
