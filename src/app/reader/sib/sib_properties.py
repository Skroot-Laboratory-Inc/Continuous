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
    def getContinuousProperties():
        """Sib Properties for Continuous (Manufacturing) use case."""
        return SibProperties(
            startFrequency=100,
            stopFrequency=160,
        )

    @staticmethod
    def getFlowCellProperties():
        """SIB properties for Flow Cell use case."""
        return SibProperties(
            startFrequency=70,
            stopFrequency=120,
        )

    @staticmethod
    def getRollerBottleProperties():
        """SIB properties for Flow Cell use case."""
        return SibProperties(
            startFrequency=120,
            stopFrequency=160,
        )

    @staticmethod
    def getTunairProperties():
        """SIB properties for Flow Cell use case."""
        return SibProperties(
            startFrequency=100,
            stopFrequency=160,
            stepSize=0.1,
            repeatMeasurements=80,
        )
