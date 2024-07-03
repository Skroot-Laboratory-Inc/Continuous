class SecondAxisDataPoint:
    def __init__(self, time, value):
        self.secondAxisTime = time
        self.secondAxisValue = value

    def getTime(self):
        return self.secondAxisTime

    def getValue(self):
        return self.secondAxisValue
