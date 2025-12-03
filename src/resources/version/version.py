from enum import Enum

from src.app.ui_manager.theme.theme_manager import Theme


class DevelopmentVersion(Enum):
    Dev = "Dev"
    Test = "Test"
    Production = "Prod"


class UseCase(Enum):
    Manufacturing = "Manufacturing"
    FlowCell = "FlowCell"
    Tunair = "Tunair"
    RollerBottle = "RollerBottle"


class Version:
    def __init__(self):
        self.majorVersion = 3.0
        self.minorVersion = 0
        self.theme = Theme.Skroot
        self.useCase = UseCase.RollerBottle
        self.developmentVersion = DevelopmentVersion.Dev
        self.isBeta = True

    def getMajorVersion(self) -> float:
        return self.majorVersion

    def getMinorVersion(self) -> int:
        return self.minorVersion

    def getUseCase(self) -> str:
        return self.useCase.value

    def getTheme(self) -> Theme:
        return self.theme

    def getReleaseBucket(self) -> str:
        if self.isBeta:
            return f"{self.useCase.value}/{self.developmentVersion.value}/Beta"
        else:
            return f"{self.useCase.value}/{self.developmentVersion.value}"

