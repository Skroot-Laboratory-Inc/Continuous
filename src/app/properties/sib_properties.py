from src.app.properties.common_properties import CommonProperties


class SibProperties:
    def __init__(self):
        self.calibrationStartFreq = CommonProperties().defaultStartFrequency
        self.calibrationStopFreq = CommonProperties().defaultEndFrequency
        self.stepSize = 0.01
        self.initialSpikeMhz = 0.2
        self.yAxisLabel = 'Signal Strength (Unitless)'


