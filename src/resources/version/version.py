from enum import Enum

from src.app.ui_manager.theme.theme_manager import Theme


class DevelopmentVersion(Enum):
    Dev = "Dev"
    Test = "Test"
    Production = "Prod"


class UseCase(Enum):
    Continuous = "Manufacturing"
    FlowCell = "FlowCell"
    Tunair = "Tunair"
    RollerBottle = "RollerBottle"


class Version:
    def __init__(self):
        self.versions = {
            UseCase.Continuous: {"major": 3.0, "minor": 5},
            UseCase.FlowCell: {"major": 3.0, "minor": 5},
            UseCase.Tunair: {"major": 3.0, "minor": 5},
            UseCase.RollerBottle: {"major": 3.0, "minor": 5}
        }

        self.theme = Theme.IBI
        self.useCase = UseCase.Continuous
        self.developmentVersion = DevelopmentVersion.Dev
        self.isBeta = True

    def getMajorVersion(self) -> float:
        """Get major version for a specific use case or current use case"""
        return self.versions[self.useCase]["major"]

    def getMinorVersion(self) -> int:
        """Get minor version for a specific use case or current use case"""
        return self.versions[self.useCase]["minor"]

    def getVersionString(self) -> str:
        """Get version string (e.g., '3.0.4') for a specific use case"""
        major = self.versions[self.useCase]["major"]
        minor = self.versions[self.useCase]["minor"]
        return f"{major}.{minor}"

    def getReleaseNotesFilePath(self) -> str:
        """Get the file path for release notes of a specific use case"""
        return f"../resources/version/release_notes/{self.getUseCase()}.json"

    def getUseCase(self) -> str:
        return self.useCase.value

    def getTheme(self) -> Theme:
        return self.theme

    def getReleaseBucket(self) -> str:
        if self.isBeta:
            return f"{self.getUseCase()}/{self.developmentVersion.value}/Beta"
        else:
            return f"{self.getUseCase()}/{self.developmentVersion.value}"

