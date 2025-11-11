from src.app.reader.analyzer.secondary_axis_tracker import SecondaryAxisTracker


class DevSecondaryAxisTracker(SecondaryAxisTracker):
    def __init__(self, outputFile: str):
        super().__init__(outputFile)

    def getTimes(self, startTime: int) -> [float]:
        return [0, 1.2, 3.1, 4.2, 7.8, 9.2, 10.3, 12.2]

    def getValues(self) -> [float]:
        return [0, 0.3, 0.5, 1.2, 13, 19, 23, 24]
