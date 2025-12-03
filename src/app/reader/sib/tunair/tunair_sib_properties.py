from src.app.reader.sib.sib_properties import SibProperties


class TunairSibProperties(SibProperties):
    def __init__(self):
        super().__init__()
        self.stepSize = 0.1
