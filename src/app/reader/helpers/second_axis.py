import csv
import logging
from tkinter import simpledialog

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.model.second_axis.second_axis_data_point import SecondAxisDataPoint
from src.app.model.second_axis.second_axis_result import SecondAxisResult


class SecondAxis:
    def __init__(self, readerNumber, secondAxisTitle, FileManager: ReaderFileManager):
        self.SecondAxisResult = SecondAxisResult(secondAxisTitle, [], [])
        self.readerNumber = readerNumber
        self.FileManager = FileManager

    def typeSecondAxisValues(self, timeVector):
        value = simpledialog.askfloat(
            f'Reader {self.readerNumber} {self.SecondAxisResult.getTitle()}',
            f'Enter the value for {self.SecondAxisResult.getTitle()} and reader {self.readerNumber} here. \n Numbers only')
        if value is not None:
            if len(timeVector) > 0:
                secondAxisDataPoint = SecondAxisDataPoint(timeVector[-1], value)
            else:
                secondAxisDataPoint = SecondAxisDataPoint(0, value)
            self.SecondAxisResult.appendPoint(secondAxisDataPoint)
            with open(self.FileManager.getSecondAxis(), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time (hours)', self.SecondAxisResult.getTitle()])
                writer.writerows(zip(self.SecondAxisResult.getTime(), self.SecondAxisResult.getValues()))
            logging.info(f'second axis value for Reader {self.readerNumber} entered: {value}')

    def getTime(self):
        return self.SecondAxisResult.getTime()

    def getValues(self):
        return self.SecondAxisResult.getValues()

    def getTitle(self):
        return self.SecondAxisResult.getTitle()
