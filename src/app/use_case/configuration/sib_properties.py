from dataclasses import dataclass


@dataclass
class SibProperties:
    startFrequency: float
    stopFrequency: float
    stepSize: float = 0.01
    initialSpikeMhz: float = 0.2
    yAxisLabel: str = 'Signal Strength (Unitless)'
    repeatMeasurements: int = 1

    @staticmethod
    def getWWContinuousProperties():
        """Sib Properties for WWContinuous use case."""
        return SibProperties(
            startFrequency=100,
            stopFrequency=160,
            stepSize=0.2
        )

    @staticmethod
    def getSkrootContinuousProperties():
        """Sib Properties for SkrootContinuous use case."""
        return SibProperties(
            startFrequency=100,
            stopFrequency=160,
            stepSize=0.2
        )

    @staticmethod
    def getFlowCellProperties():
        """SIB configuration for Flow Cell use case."""
        return SibProperties(
            startFrequency=70,
            stopFrequency=120,
            stepSize=0.2
        )

    @staticmethod
    def getSkrootFlowCellProperties():
        """SIB configuration for Skroot Flow Cell use case."""
        return SibProperties(
            startFrequency=110,
            stopFrequency=160,
            stepSize=0.2
        )

    @staticmethod
    def getRollerBottleProperties():
        """SIB configuration for Flow Cell use case."""
        return SibProperties(
            startFrequency=120,
            stopFrequency=160,
        )

    @staticmethod
    def getTunairProperties():
        """SIB configuration for Flow Cell use case."""
        return SibProperties(
            startFrequency=100,
            stopFrequency=160,
            stepSize=0.2,
            repeatMeasurements=80,
        )
