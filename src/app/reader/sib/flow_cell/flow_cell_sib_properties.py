from src.app.reader.sib.sib_properties import SibProperties


class FlowCellSibProperties(SibProperties):
    def __init__(self):
        super().__init__()
        self.calibrationStartFreq = 70
        self.calibrationStopFreq = 120
        self.defaultStartFrequency = 70
        self.defaultEndFrequency = 120
