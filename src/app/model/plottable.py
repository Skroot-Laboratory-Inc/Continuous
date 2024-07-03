class Plottable:
    def __init__(self, xValues, yValues, color):
        self.xValues = xValues
        self.yValues = yValues
        self.color = color

    def getXValues(self):
        return self.xValues

    def getYValues(self):
        return self.yValues

    def getColor(self):
        return self.color