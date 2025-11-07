import csv
from itertools import zip_longest

import numpy as np

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.helper_functions import getCpuTemp


class TemperatureResultSet:
    def __init__(self, readerFileManager: ReaderFileManager):
        self.timestampsColumn = "timestamps"
        self.temperaturesColumn = "Temperature (C)"
        self.readerFileManager = readerFileManager
        self.timestamps, self.temperatures = [], []

    def appendTemp(self, timestamp: int):
        self.timestamps.append(timestamp)
        self.temperatures.append(getCpuTemp())
        self.writeToFile()

    def writeToFile(self):
        with open(self.readerFileManager.getTemperatureCsv(), 'w', newline='') as f:
            writer = csv.writer(f)
            rowHeaders = []
            rowData = []
            rowHeaders.append(self.timestampsColumn)
            rowData.append(self.timestamps)
            rowHeaders.append(self.temperaturesColumn)
            rowData.append(self.temperatures)
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))