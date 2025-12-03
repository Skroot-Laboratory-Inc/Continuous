from src.app.reader.sib.sib_properties import SibProperties


class RollerBottleSibProperties(SibProperties):
    def __init__(self):
        super().__init__()
        self.defaultStartFrequency = 120
