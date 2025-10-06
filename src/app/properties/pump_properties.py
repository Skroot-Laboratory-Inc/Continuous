class PumpProperties:
    def __init__(self):
        self.stepsPerRevolution = 360 / 1.8  # 1.8 degrees per step
        self.defaultFlowRate = 10
        self.primingFlowRate = 300
        self.millilitersPerRevolution = 0.0803
