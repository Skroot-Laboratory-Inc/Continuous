from src.app.properties.pump_properties import PumpProperties


def flowRateToStepPeriod(flowRate: float) -> float:
    """Convert flow rate in mL/hr to step delay in seconds"""
    return rpmToStepPeriod(flowRateToRpm(flowRate))


def flowRateToRpm(flowRate: float) -> float:
    """Convert flow rate in mL/hr to RPM"""
    return (flowRate * 60) / PumpProperties().millilitersPerRevolution


def rpmToStepPeriod(rpm: float) -> float:
    """Convert RPM to step delay in seconds"""
    return 60 / (rpm * PumpProperties().stepsPerRevolution)
