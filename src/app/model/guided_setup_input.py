from src.app.properties.guided_setup_defaults import GuidedSetupDefaults


class GuidedSetupInput:
    def __init__(self):
        guidedSetupDefaults = GuidedSetupDefaults()
        self.month = guidedSetupDefaults.month
        self.day = guidedSetupDefaults.day
        self.year = guidedSetupDefaults.year
        self.numReaders = guidedSetupDefaults.numReaders
        self.scanRate = guidedSetupDefaults.scanRate
        self.calibrate = guidedSetupDefaults.calibrate
        self.secondAxisTitle = guidedSetupDefaults.secondAxisTitle
        self.experimentId = guidedSetupDefaults.experimentId
        self.equilibrationTime = guidedSetupDefaults.equilibrationTime
        self.savePath = ""

    def getMonth(self):
        return self.month

    def getDay(self):
        return self.day

    def getYear(self):
        return self.year

    def getDate(self):
        return f"{self.month}-{self.day}-{self.year}"

    def getNumReaders(self):
        return int(self.numReaders)

    def getScanRate(self):
        return float(self.scanRate)

    def getCalibrate(self):
        return self.calibrate

    def getSecondAxis(self):
        return self.secondAxisTitle

    def getExperimentId(self):
        return self.experimentId

    def getEquilibrationTime(self):
        return float(self.equilibrationTime)

    def getSavePath(self):
        return self.savePath

    def setSavePath(self, savePath):
        self.savePath = savePath

