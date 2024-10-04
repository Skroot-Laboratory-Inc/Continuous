from enum import Enum


class ReleaseBucket(Enum):
    Dev = "Dev"
    RnDTest = "R&D-Test"
    RnDProduction = "R&D-Prod"
    CustomerTest = "Customer-Test"
    CustomerProduction = "Customer-Prod"


class Version:
    def __init__(self):
        self.majorVersion = 2.5
        self.minorVersion = 42
        self.releaseBucket = ReleaseBucket.RnDTest

    def getMajorVersion(self) -> float:
        return self.majorVersion

    def getMinorVersion(self) -> int:
        return self.minorVersion

    def getReleaseBucket(self) -> str:
        return self.releaseBucket.value

