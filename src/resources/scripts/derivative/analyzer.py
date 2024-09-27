import csv
import glob
import os
from itertools import zip_longest

import numpy as np
import pandas
from matplotlib import pyplot as plt

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.reader.analyzer.analyzer import Analyzer


class DerivativeAnalyzer:
    def __init__(self, experimentFolderDirectory, equilibrationTime):
        self.equilibrationTime = equilibrationTime
        self.experimentFolderDirectory = experimentFolderDirectory
        self.postProcessingLocation = f'{self.experimentFolderDirectory}/Post Processing'
        if not os.path.exists(self.postProcessingLocation):
            os.mkdir(self.postProcessingLocation)
        self.readerDirectories = [folder for folder in sorted(glob.glob(f'{self.experimentFolderDirectory}/**/')) if "Post Processing" not in folder and "Analysis" not in folder and "Log" not in folder]
        self.analyzedFileMap = {}
        self.resultMap = {}

    def loadReaderAnalyzed(self):
        for directory in self.readerDirectories:
            self.analyzedFileMap[os.path.basename(os.path.dirname(directory))] = f'{directory}/smoothAnalyzed.csv'

    def calculateDerivative(self):
        analyzer = Analyzer(ReaderFileManager("", 1))
        for readerId, readerAnalyzed in self.analyzedFileMap.items():
            readings = pandas.read_csv(readerAnalyzed)
            readerTime = readings['Time (hours)'].values.tolist()
            readerSGI = readings['Skroot Growth Index (SGI)'].values.tolist()
            readerTimeCopy = readerTime.copy()
            readerSGICopy = readerSGI.copy()
            for index, value in enumerate(readerTime):
                if value < self.equilibrationTime:
                    readerTimeCopy.remove(value)
                    readerSGICopy.remove(readerSGI[index])
            cubicValues, derivativeValues = analyzer.calculateDerivativeValues(readerTimeCopy, readerSGICopy)
            potentialHarvestTime = readerTime[derivativeValues.index(max(derivativeValues))]

            if readerTimeCopy.index(potentialHarvestTime) < 0.99*len(readerTimeCopy):
                plt.axvline(x=potentialHarvestTime)
            plt.scatter(readerTimeCopy, cubicValues, color='tab:blue')
            plt.scatter(readerTimeCopy, readerSGICopy, color='k', s=4)
            plt.ylabel("Skroot Growth Index  (SGI)", color='tab:blue')
            plt.xlabel("Time (hours)", color='k')
            plt.title(readerId)
            ax2 = plt.twinx()
            ax2.scatter(readerTimeCopy, derivativeValues, color='tab:orange')
            ax2.set_ylabel("Skroot Growth Rate  (SGR)", color='tab:orange')
            plt.savefig(f"{os.path.dirname(os.path.dirname(readerAnalyzed))}/Post Processing/{readerId}.jpg")
            plt.clf()
            self.resultMap[readerId] = {
                "time": readerTimeCopy,
                "sgi": readerSGICopy,
                "cubic": cubicValues,
                "derivative": derivativeValues
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
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))
