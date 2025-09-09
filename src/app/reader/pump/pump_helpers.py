from src.app.properties.pump_properties import PumpProperties


def flowRateToStepPeriod(flowRate: float) -> float:
    """Convert RPM to step delay"""
    return rpmToStepPeriod(flowRateToRpm(flowRate))


def flowRateToRpm(flowRate: float) -> float:
    """Convert RPM to step delay"""
    return flowRate / PumpProperties().millilitersPerRevolution


def rpmToStepPeriod(rpm: float) -> float:
    """Convert RPM to step delay"""
    return 60 / (rpm * PumpProperties().stepsPerRevolution)
