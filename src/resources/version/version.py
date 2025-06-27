from enum import Enum


class DevelopmentVersion(Enum):
    Dev = "Dev"
    Test = "Test"
    Production = "Prod"


class UseCase(Enum):
    RnD = "R&D"
    Manufacturing = "Manufacturing"
    BenchTop = "BenchTop"


class Version:
    def __init__(self):
        self.majorVersion = 1.2
        self.minorVersion = 1
        self.useCase = UseCase.Manufacturing
        self.developmentVersion = DevelopmentVersion.Test

    def getMajorVersion(self) -> float:
        return self.majorVersion

    def getMinorVersion(self) -> int:
        return self.minorVersion

    def getUseCase(self) -> str:
        return self.useCase.value

    def getReleaseBucket(self) -> str:
        return f"{self.useCase.value}/{self.developmentVersion.value}"

