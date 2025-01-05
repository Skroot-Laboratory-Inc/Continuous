import csv
import glob
import os
from datetime import datetime
from itertools import zip_longest

import numpy as np
import pandas
from matplotlib import pyplot as plt

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import datetimeToMillis
from src.app.model.result_set.result_set import ResultSet
from src.app.model.result_set.result_set_data_point import ResultSetDataPoint
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
        for readerId, readerAnalyzed in self.analyzedFileMap.items():
            harvestAlgorithm = HarvestAlgorithm(ReaderFileManager("", 1))
            readings = pandas.read_csv(readerAnalyzed)
            try:
                readerTime = [datetimeToMillis(datetime.strptime(time, "%m/%y/%Y  %I:%M:%S %p"))/3600000 for time in readings['Timestamp'].values.tolist()]
            except:
                try:
                    readerTime = [datetimeToMillis(datetime.fromisoformat(time))/3600000 for time in readings['Timestamp'].values.tolist()]
                except:
                    readerTime = [time/3600000 for time in readings['Timestamp'].values.tolist()]
            startTime = readerTime[0]
            timeInHours = [time - startTime for time in readerTime]
            readerSGI = readings['Skroot Growth Index (SGI)'].values.tolist()
            resultSet = ResultSet()
            for index in range(len(readerSGI)):
                derivativeValue = analyzer.calculateDerivativeValues(
                    timeInHours[:index],
                    readerSGI[:index],
                )
                dataPoint = ResultSetDataPoint(resultSet)
                dataPoint.setDerivative(derivativeValue)
                dataPoint.setTime(timeInHours[:index+1])
                resultSet.setValues(dataPoint)
                harvestAlgorithm.check(resultSet)
            plt.title(readerId)
            plt.xlabel("Time Since Equilibration", color='k')
            fig, ax = plt.subplots()
            ax2 = ax.twinx()
            ax.scatter(timeInHours, readerSGI, color='k', s=4)
            ax.set_ylabel("Skroot Growth Index  (SGI)", color='tab:blue')
            ax2.scatter(timeInHours[:len(resultSet.smoothDerivativeMean)], resultSet.smoothDerivativeMean, color='tab:orange')
            ax2.set_ylabel("Derivative Mean", color='tab:orange')
            plt.savefig(f"{os.path.dirname(os.path.dirname(readerAnalyzed))}/Post Processing/{readerId}.jpg")
            plt.clf()
            self.resultMap[readerId] = {
                "time": timeInHours,
                "sgi": readerSGI,
                "derivative": resultSet.smoothDerivativeMean,
                "peak": harvestAlgorithm.historicalCentroid,
                "std": harvestAlgorithm.historicalStd,
                "rSquared": harvestAlgorithm.historicalRSquared,
                "harvest": harvestAlgorithm.historicalHarvestTime,
                "timeToHarvest": harvestAlgorithm.historicalTimeToHarvest,
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
                rowHeaders.append(f'Peak {readerId} ')
                rowData.append(results["peak"])
                rowHeaders.append(f'Std {readerId} ')
                rowData.append(results["std"])
                rowHeaders.append(f'R Squared {readerId} ')
                rowData.append(results["rSquared"])
                rowHeaders.append(f'Harvest Time {readerId} ')
                rowData.append(results["harvest"])
                rowHeaders.append(f'Time To Harvest {readerId} ')
                rowData.append(results["timeToHarvest"])
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))

    @staticmethod
    def sortFn(folderDirectory):
        return int(os.path.basename(os.path.dirname(folderDirectory)).replace("Reader ", ""))
