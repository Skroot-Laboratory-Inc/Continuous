from src.app.properties.pump_properties import PumpProperties


# TODO: flowRateToRpm and rpmToFlowRate are not inverses — the codebase mixes
# RPM and mL/hr under the name "flowRate" (e.g. setFlowRate is called with RPM
# values). Reconcile the units and rename the affected callers/parameters.
def flowRateToStepPeriod(flowRate: float) -> float:
    """Convert flow rate in mL/hr to step delay in seconds"""
    return rpmToStepPeriod(flowRateToRpm(flowRate))


def flowRateToRpm(flowRate: float) -> float:
    """Convert flow rate in mL/hr to RPM"""
    return (flowRate * 60) / PumpProperties().millilitersPerRevolution


def rpmToStepPeriod(rpm: float) -> float:
    """Convert RPM to step delay in seconds"""
    return 60 / (rpm * PumpProperties().stepsPerRevolution)


def rpmToFlowRate(rpm: float) -> float:
    """Convert RPM to flow rate in mL/hr"""
    return rpm * PumpProperties().millilitersPerRevolution * 60
