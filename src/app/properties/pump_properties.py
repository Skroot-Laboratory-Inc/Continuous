class PumpProperties:
    def __init__(self):
        self.microsteps = 8  # 1/8 microstepping
        self.stepAngle = 1.8
        self.stepsPerRevolution = int(360 / self.stepAngle * self.microsteps)
        self.defaultFlowRate = 2
        self.defaultPrimingFlowRate = 100
        self.millilitersPerRevolution = 0.0803
