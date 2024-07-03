from src.app.model.second_axis_data_point import SecondAxisDataPoint


class SecondAxisResult:
    def __init__(self, title, time, values):
        self.title = title
        self.secondAxisTime = time
        self.secondAxisValues = values

    def getTitle(self):
        return self.title

    def getTime(self):
        return self.secondAxisTime

    def getValues(self):
        return self.secondAxisValues

    def appendPoint(self, point: SecondAxisDataPoint):
        self.secondAxisValues.append(point.getValue())
        self.secondAxisTime.append(point.getTime())
