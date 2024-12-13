import csv
import glob
import os
from datetime import datetime, date
from itertools import zip_longest

import numpy as np
import pandas
from matplotlib import pyplot as plt

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import datetimeToMillis, millisToDatetime
from src.app.model.result_set.result_set import ResultSet
from src.app.model.result_set.result_set_data_point import ResultSetDataPoint
from src.app.properties.harvest_properties import HarvestProperties
from src.app.reader.algorithm.harvest_algorithm import HarvestAlgorithm
from src.app.reader.analyzer.analyzer import Analyzer


class DerivativeAnalyzer:
    def __init__(self, experimentFolderDirectory):
        self.experimentFolderDirectory = experimentFolderDirectory
        self.postProcessingLocation = f'{self.experimentFolderDirectory}/Post Processing'
        if not os.path.exists(self.postProcessingLocation):
            os.mkdir(self.postProcessingLocation)
        self.readerDirectories = [folder for folder in glob.glob(f'{self.experimentFolderDirectory}/Reader **/')]
        self.readerDirectories.sort(key=self.sortFn)
        self.analyzedFileMap = {}
        self.resultMap = {}

    def loadReaderAnalyzed(self):
        for directory in self.readerDirectories:
            self.analyzedFileMap[os.path.basename(os.path.dirname(directory))] = f'{directory}/smoothAnalyzed.csv'

    def calculateDerivative(self):
        analyzer = Analyzer(ReaderFileManager("", 1))
        harvestAlgorithm = HarvestAlgorithm(ReaderFileManager("", 1))
        for readerId, readerAnalyzed in self.analyzedFileMap.items():
            readings = pandas.read_csv(readerAnalyzed)
            try:
                readerTime = [datetimeToMillis(datetime.strptime(time, "%m/%y/%Y  %I:%M:%S %p"))/3600000 for time in readings['Timestamp'].values.tolist()]
            except:
                readerTime = [datetimeToMillis(datetime.fromisoformat(time))/3600000 for time in readings['Timestamp'].values.tolist()]
            startTime = readerTime[0]
            timeInHours = [time - startTime for time in readerTime]
            readerSGI = readings['Skroot Growth Index (SGI)'].values.tolist()
            resultSet = ResultSet()
            for index in range(len(readerSGI)):
                derivativeValue, secondDerivativeValue = analyzer.calculateDerivativeValues(
                    timeInHours[:index],
                    readerSGI[:index],
                    resultSet.derivative
                )
                dataPoint = ResultSetDataPoint(resultSet)
                dataPoint.setDerivative(derivativeValue)
                dataPoint.setSecondDerivative(secondDerivativeValue)
                resultSet.setValues(dataPoint)

            plt.title(readerId)
            plt.xlabel("Time Since Equilibration", color='k')
            fig, ax = plt.subplots()
            fig.subplots_adjust(right=0.75)
            ax2 = ax.twinx()
            ax3 = ax.twinx()
            ax3.spines.right.set_position(("axes", 1.2))
            ax2.spines.right.set_position(("axes", 1))
            ax.scatter(timeInHours, readerSGI, color='k', s=4)
            ax.set_ylabel("Skroot Growth Index  (SGI)", color='tab:blue')
            ax2.scatter(timeInHours[:len(resultSet.getDerivativeMean())], resultSet.getDerivativeMean(), color='tab:orange')
            ax2.set_ylabel("Derivative Mean", color='tab:orange')
            ax3.scatter(timeInHours[:len(resultSet.getSecondDerivativeMean())], resultSet.getSecondDerivativeMean(), color='tab:red')
            ax3.set_ylabel("Second Derivative Mean", color='tab:red')
            plt.savefig(f"{os.path.dirname(os.path.dirname(readerAnalyzed))}/Post Processing/{readerId}.jpg")
            plt.clf()
            self.resultMap[readerId] = {
                "time": timeInHours,
                "sgi": readerSGI,
                "derivative": resultSet.getDerivativeMean(),
                "secondDerivative": resultSet.getSecondDerivativeMean(),
            }

    def createDerivativeSummaryAnalyzed(self):
        rowHeaders = []
        rowData = []

        with open(f"{self.postProcessingLocation}/derivativeSummaryAnalyzed.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            for readerId, results in self.resultMap.items():
                rowHeaders.append(f'Time {readerId} ')
                rowData.append(results["time"])
                rowHeaders.append(f'SGI {readerId} ')
                rowData.append(results["sgi"])
                rowHeaders.append(f'Derivative {readerId} ')
                rowData.append(results["derivative"])
                rowHeaders.append(f'Second Derivative {readerId} ')
                rowData.append(results["secondDerivative"])
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))

    @staticmethod
    def sortFn(folderDirectory):
        return int(os.path.basename(os.path.dirname(folderDirectory)).replace("Reader ", ""))
