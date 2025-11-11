from enum import Enum


class DevelopmentVersion(Enum):
    Dev = "Dev"
    Test = "Test"
    Production = "Prod"


class UseCase(Enum):
    RnD = "R&D"
    Manufacturing = "Manufacturing"
    BenchTop = "BenchTop"
    FlowCell = "FlowCell"


class Version:
    def __init__(self):
        self.majorVersion = 1.0
        self.minorVersion = 7
        self.useCase = UseCase.FlowCell
        self.developmentVersion = DevelopmentVersion.Dev

    def getMajorVersion(self) -> float:
        return self.majorVersion

    def getMinorVersion(self) -> int:
        return self.minorVersion

    def getUseCase(self) -> str:
        return self.useCase.value

    def getReleaseBucket(self) -> str:
        return f"{self.useCase.value}/{self.developmentVersion.value}"

