from src.app.properties.pump_properties import PumpProperties


def rpmToStepPeriod(rpm: float) -> float:
    """Time between motor steps (s) for a given motor RPM."""
    return 60 / (rpm * PumpProperties().stepsPerRevolution)


def rpmToCommandedFlowRate(rpm: float) -> float:
    """Volumetric flow rate the pump is commanded to deliver (mL/hr) at the
    given motor RPM, ignoring system losses."""
    return rpm * PumpProperties().millilitersPerRevolution * 60


def commandedToActualFlowRate(commandedFlowRate: float) -> float:
    """Actual delivered flow rate (mL/hr) for a given commanded flow rate
    (mL/hr), applying the lossy quadratic fit characterised in SUP-4."""
    properties = PumpProperties()
    return (properties.flowLossQuadratic * commandedFlowRate ** 2
            + properties.flowLossLinear * commandedFlowRate)


def rpmToActualFlowRate(rpm: float) -> float:
    """Actual delivered flow rate (mL/hr) for a given motor RPM, accounting
    for the lossy pump system."""
    return commandedToActualFlowRate(rpmToCommandedFlowRate(rpm))
