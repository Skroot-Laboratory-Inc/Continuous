from src.app.reader.analyzer.secondary_axis_tracker import SecondaryAxisTracker


class DevSecondaryAxisTracker(SecondaryAxisTracker):
    def __init__(self, outputFile: str):
        super().__init__(outputFile)

    def getTimes(self, startTime: int) -> [float]:
        return [1, 5, 8, 10, 28, 30, 39, 53]

    def getValues(self) -> [float]:
        return [0, 6, 9.5, 11, 22, 24, 18, 20]
