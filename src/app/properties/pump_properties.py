class PumpProperties:
    def __init__(self):
        self.microsteps = 8  # 1/8 microstepping
        self.stepsPerRevolution = int(360 / (1.8 * self.microsteps))  # 1.8 degrees per step
        self.defaultFlowRate = 10
        self.primingFlowRate = 300
        self.millilitersPerRevolution = 0.0803
