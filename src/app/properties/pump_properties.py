class PumpProperties:
    def __init__(self):
        self.microsteps = 8  # 1/8 microstepping
        self.stepAngle = 1.8
        self.stepsPerRevolution = int(360 / self.stepAngle * self.microsteps)
        self.defaultRpm = 2
        self.primingRpm = 100
        self.millilitersPerRevolution = 0.0417

        # Empirical fit from SUP-4 characterising delivered flow vs. set flow:
        #   actualMlPerHr = lossQuadratic * setMlPerHr**2 + lossLinear * setMlPerHr
        # Captures the lossy behaviour of the pump system above ~100 mL/hr.
        self.flowLossQuadratic = -0.00115
        self.flowLossLinear = 0.9875
