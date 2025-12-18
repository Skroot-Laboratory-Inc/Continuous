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
        # Per-use-case versioning
        self.versions = {
            UseCase.Continuous: {"major": 3.0, "minor": 4},
            UseCase.FlowCell: {"major": 3.0, "minor": 4},
            UseCase.Tunair: {"major": 3.0, "minor": 4},
            UseCase.RollerBottle: {"major": 3.0, "minor": 4}
        }

        # Legacy single version (deprecated - use versions dict)
        self.majorVersion = 3.0
        self.minorVersion = 4

        self.theme = Theme.IBI
        self.useCase = UseCase.FlowCell
        self.developmentVersion = DevelopmentVersion.Test
        self.isBeta = True

    def getMajorVersion(self, use_case: UseCase = None) -> float:
        """Get major version for a specific use case or current use case"""
        if use_case is None:
            use_case = self.useCase
        return self.versions[use_case]["major"]

    def getMinorVersion(self, use_case: UseCase = None) -> int:
        """Get minor version for a specific use case or current use case"""
        if use_case is None:
            use_case = self.useCase
        return self.versions[use_case]["minor"]

    def getVersionString(self, use_case: UseCase = None) -> str:
        """Get version string (e.g., 'v3.0.4') for a specific use case"""
        if use_case is None:
            use_case = self.useCase
        major = self.versions[use_case]["major"]
        minor = self.versions[use_case]["minor"]
        return f"v{major}.{minor}"

    def setVersion(self, use_case: UseCase, major: float, minor: int):
        """Set version for a specific use case"""
        self.versions[use_case]["major"] = major
        self.versions[use_case]["minor"] = minor

    def getAllVersions(self) -> dict:
        """Get all use case versions"""
        return {
            use_case: {
                "major": data["major"],
                "minor": data["minor"],
                "version_string": f"v{data['major']}.{data['minor']}"
            }
            for use_case, data in self.versions.items()
        }

    def getReleaseNotesFilePath(self, use_case: UseCase = None) -> str:
        """Get the file path for release notes of a specific use case"""
        if use_case is None:
            use_case = self.useCase
        return f"../resources/version/release-notes-{use_case.value}.json"

    def getUseCase(self) -> str:
        return self.useCase.value

    def getTheme(self) -> Theme:
        return self.theme

    def getReleaseBucket(self) -> str:
        if self.isBeta:
            return f"{self.useCase.value}/{self.developmentVersion.value}/Beta"
        else:
            return f"{self.useCase.value}/{self.developmentVersion.value}"

