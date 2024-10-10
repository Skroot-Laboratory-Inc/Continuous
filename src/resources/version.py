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
        self.minorVersion = 0
        self.useCase = UseCase.Manufacturing
        self.developmentVersion = DevelopmentVersion.Production

    def getMajorVersion(self) -> float:
        return self.majorVersion

    def getMinorVersion(self) -> int:
        return self.minorVersion

    def getUseCase(self) -> str:
        return self.useCase.value

    def getReleaseBucket(self) -> str:
        if self.developmentVersion == DevelopmentVersion.Dev:
            return self.developmentVersion.value
        else:
            return f"{self.useCase.value}-{self.developmentVersion.value}"

