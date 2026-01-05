"""Configuration for setup forms across different use cases."""
from dataclasses import dataclass
from typing import List


@dataclass
class SetupFormConfig:
    """Configuration for a setup form that defines which options are available."""

    scanRateOptions: List[str]
    equilibrationTimeOptions: List[str]
    defaultScanRate: str
    defaultEquilibrationTime: str = "24"
    defaultCalibrate: bool = True

    @staticmethod
    def getContinuousConfig():
        """Configuration for Continuous (Manufacturing) use case."""
        return SetupFormConfig(
            scanRateOptions=["2", "5", "10", "30", "60"],
            equilibrationTimeOptions=["0", "0.2", "2", "12", "24"],
            defaultScanRate="2",
            defaultEquilibrationTime="0",
        )

    @staticmethod
    def getFlowCellConfig():
        """Configuration for FlowCell use case."""
        return SetupFormConfig(
            scanRateOptions=["2", "5", "10", "30", "60"],
            equilibrationTimeOptions=["0", "0.2", "2", "12", "24"],
            defaultScanRate="5",
        )

    @staticmethod
    def getRollerBottleConfig():
        """Configuration for RollerBottle use case."""
        return SetupFormConfig(
            scanRateOptions=["5", "10", "30", "60"],
            equilibrationTimeOptions=["0", "0.2", "2", "12", "24"],
            defaultScanRate="10",
        )

    @staticmethod
    def getTunairConfig():
        """Configuration for Tunair use case."""
        return SetupFormConfig(
            scanRateOptions=["10", "30", "60"],
            equilibrationTimeOptions=["0", "0.2", "2", "12", "24"],
            defaultScanRate="30",
        )
