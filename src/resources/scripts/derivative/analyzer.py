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
            cubicValues = []
            derivativeValues = []
            secondDerivativeValues = []
            stdValues = []
            peakValues = []
            for index in range(len(readerSGI)):
                cubicValue, derivativeValue, secondDerivativeValue = analyzer.calculateDerivativeValues(
                    timeInHours[:index],
                    readerSGI[:index],
                )
                cubicValues.append(cubicValue)
                derivativeValues.append(derivativeValue)
                secondDerivativeValues.append(secondDerivativeValue)
                if index > HarvestProperties().savgolPoints*2 and not np.isnan(np.nanmean(derivativeValues)):
                    center, std = harvestAlgorithm.harvestAlgorithm(
                        timeInHours[:index],
                        derivativeValues[:index],
                    )
                    peakValues.append(center)
                    stdValues.append(std)
                else:
                    peakValues.append(np.nan)
                    stdValues.append(np.nan)

            plt.scatter(timeInHours, readerSGI, color='tab:green')
            plt.scatter(timeInHours, cubicValues, color='tab:blue')
            plt.scatter(timeInHours, readerSGI, color='k', s=4)
            plt.ylabel("Skroot Growth Index  (SGI)", color='tab:blue')
            plt.xlabel("Time Since Equilibration", color='k')
            plt.title(readerId)
            ax2 = plt.twinx()
            ax2.scatter(timeInHours, derivativeValues, color='tab:orange')
            ax2.set_ylabel("Skroot Growth Rate  (SGR)", color='tab:orange')
            plt.savefig(f"{os.path.dirname(os.path.dirname(readerAnalyzed))}/Post Processing/{readerId}.jpg")
            plt.clf()
            self.resultMap[readerId] = {
                "time": timeInHours,
                "sgi": readerSGI,
                "cubic": cubicValues,
                "derivative": derivativeValues,
                "secondDerivative": secondDerivativeValues,
                "peak": peakValues,
                "std": stdValues
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
                rowHeaders.append(f'Cubic {readerId} ')
                rowData.append(results["cubic"])
                rowHeaders.append(f'Derivative {readerId} ')
                rowData.append(results["derivative"])
                rowHeaders.append(f'Second Derivative {readerId} ')
                rowData.append(results["secondDerivative"])
                rowHeaders.append(f'Peak {readerId} ')
                rowData.append(results["peak"])
                rowHeaders.append(f'Std {readerId} ')
                rowData.append(results["std"])
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))

    @staticmethod
    def sortFn(folderDirectory):
        return int(os.path.basename(os.path.dirname(folderDirectory)).replace("Reader ", ""))
