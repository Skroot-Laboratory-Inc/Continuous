from enum import Enum


class DevelopmentVersion(Enum):
    Dev = "Dev"
    Test = "Test"
    Production = "Prod"


class UseCase(Enum):
    RnD = "R&D"
    Manufacturing = "Manufacturing"


class Version:
    def __init__(self):
        self.majorVersion = 1.0
        self.minorVersion = 47
        self.useCase = UseCase.Manufacturing
        self.developmentVersion = DevelopmentVersion.Test

    def getMajorVersion(self) -> float:
        return self.majorVersion

    def getMinorVersion(self) -> int:
        return self.minorVersion

    def getUseCase(self) -> str:
        return self.useCase.value

    def getDevelopmentVersion(self):
        return self.developmentVersion.value

    def getReleaseBucket(self) -> str:
        return f"{self.useCase.value}/{self.developmentVersion.value}"

