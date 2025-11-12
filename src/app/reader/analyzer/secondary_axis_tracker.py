import csv
import os
from datetime import datetime

from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.widget.sidebar.configurations.secondary_axis_type import SecondaryAxisType
from src.app.widget.sidebar.configurations.secondary_axis_units import SecondaryAxisUnits


class SecondaryAxisTracker:
    def __init__(self, outputFile: str):
        self.axisValues: {int: float} = {}
        self.outputFile = outputFile

    def addValue(self, value: float):
        self.axisValues[datetimeToMillis(datetime.now())] = value
        self.writeToFile()

    def getTimestamps(self) -> [int]:
        return self.axisValues.keys()

    def getTimes(self, startTime: int) -> [float]:
        return [max(0, (time - startTime) / 3600000) for time in self.axisValues.keys()]

    def getValues(self) -> [float]:
        return self.axisValues.values()

    def writeToFile(self):
        if not os.path.exists(os.path.dirname(self.outputFile)):
            os.mkdir(os.path.dirname(self.outputFile))
        with open(self.outputFile, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', f"{SecondaryAxisType().getConfig()} {SecondaryAxisUnits().getAsUnit()}"])
            writer.writerows(zip(self.axisValues.keys(), self.axisValues.values()))
