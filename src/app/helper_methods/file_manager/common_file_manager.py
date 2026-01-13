import os.path

from src.app.ui_manager.theme.theme_manager import get_current_theme_name


class CommonFileManager:
    def __init__(self):
        srcDir = f"{os.path.dirname(os.path.dirname(getCwd()))}"
        theme = get_current_theme_name()
        resourcesDir = f"{srcDir}/src/resources"
        self.addIcon = rf"{resourcesDir}/media/{theme}/plus.png"
        self.poweredByLogo = rf"{resourcesDir}/media/{theme}/powered-by.png"
        self.arrowIcon = rf"{resourcesDir}/media/{theme}/arrow.png"
        self.switchOn = rf"{resourcesDir}/media/{theme}/switch-on.png"
        self.helpIconPng = rf"{resourcesDir}/media/help.png"
        self.switchOff = rf"{resourcesDir}/media/switch-off.png"
        self.profileIcon = rf"{resourcesDir}/media/profile.jpg"
        self.skrootLogo = rf"{resourcesDir}/media/squareLogo.PNG"
        self.powerIcon = rf"{resourcesDir}/media/power.png"
        self.wifiConnectedIcon = rf"{resourcesDir}/media/wifi-connected.png"
        self.wifiDisconnectedIcon = rf"{resourcesDir}/media/wifi-disconnected.png"
        self.troubleshootingDoc = rf"{resourcesDir}/media/troubleshootingDoc.pdf"
        self.advancedSettingsDoc = rf"{resourcesDir}/media/advancedSettings.pdf"
        self.userGuideDoc = rf"{resourcesDir}/media/userGuideDoc.pdf"
        self.experimentLogDir = f'{getDesktopLocation()}/Backend'
        self.tempSoftwareUpdateZip = fr'{os.path.dirname(srcDir)}/DesktopApp.zip'
        self.tempReleaseNotes = fr'{os.path.dirname(srcDir)}/temp'
        self.tempUpdateDirectory = fr'{os.path.dirname(srcDir)}/temp'
        self.tempUpdateScript = rf'{self.tempUpdateDirectory}/src/resources/scripts/update-script.sh'
        self.dataSavePath = f'{getDesktopLocation()}/Experiment Data'
        self.devBaseFolder = f'{getDesktopLocation()}/Backend/dev'

    def getHelpIcon(self):
        return self.helpIconPng

    def getSwitchOn(self):
        return self.switchOn

    def getSwitchOff(self):
        return self.switchOff

    def getAddIcon(self):
        return self.addIcon

    def getPoweredByLogo(self):
        return self.poweredByLogo

    def getArrowIcon(self):
        return self.arrowIcon

    def getPowerIcon(self):
        return self.powerIcon

    def getTempUpdateScript(self):
        return self.tempUpdateScript

    def getTempUpdateZip(self):
        return self.tempSoftwareUpdateZip

    def getTempNotes(self):
        return self.tempReleaseNotes

    def getTempSoftwareUpdatePath(self):
        return self.tempUpdateDirectory

    def getExperimentLogDir(self):
        return self.experimentLogDir

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

    def getWifiConnectedIcon(self):
        return self.wifiConnectedIcon

    def getWifiDisconnectedIcon(self):
        return self.wifiDisconnectedIcon


def getCwd():
    """ This gets the directory the app is being run from i.e. the path to main.py. """
    return os.getcwd()


def getDesktopLocation():
    """ This gets the path to the computer's desktop. """
    try:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except KeyError:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
