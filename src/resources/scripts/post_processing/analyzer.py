import csv
import glob
import os
from itertools import zip_longest
from pathlib import Path

import numpy as np
import pandas
from progress.bar import IncrementalBar

from src.app.exception.analysis_exception import AnalysisException
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import frequencyToIndex, getZeroPoint
from src.app.model.sweep_data import SweepData
from src.app.reader.algorithm.harvest_algorithm import HarvestAlgorithm
from src.app.reader.analyzer.analyzer import Analyzer


class PostProcessingAnalyzer:
    def __init__(self, experimentFolderDirectory, equilibrationTime):
        self.equilibrationTime = equilibrationTime
        self.experimentFolderDirectory = experimentFolderDirectory
        self.summaryAnalyzedLocation = f'{self.experimentFolderDirectory}/Post Processing'
        self.readerDirectories = [folder for folder in glob.glob(f'{self.experimentFolderDirectory}/Reader **/')]
        self.readerDirectories.sort(key=self.sortFn)
        self.rawDataScansMap = {}
        self.resultSetMap = {}
        self.zeroPointMap = {}

    def getScansForReaders(self):
        for directory in self.readerDirectories:
            allFiles = sorted(glob.glob(f'{directory}/*.csv'))
            rawDataScans = self.getAllNumberedFiles(allFiles)
            self.rawDataScansMap[os.path.basename(os.path.dirname(directory))] = rawDataScans

    def analyzeReaderScans(self):
        for readerId, rawDataFiles in self.rawDataScansMap.items():
            readerFileManager = ReaderFileManager("", 1)
            analyzer = Analyzer(readerFileManager, HarvestAlgorithm(readerFileManager))
            setZeroPoint = False
            zeroPoint = 1
            readerProgressBar = IncrementalBar(
                f'{readerId}',
                suffix='%(percent)d%%',
                max=len(rawDataFiles))
            for file in rawDataFiles:
                readerProgressBar.next()
                readerFileManager.scanNumber = float(Path(os.path.basename(file)).stem)
                readerFileManager.readerSavePath = os.path.dirname(file)
                scanReadings = pandas.read_csv(file)
                sweepData = SweepData(
                    scanReadings['Frequency (MHz)'].values.tolist(),
                    scanReadings['Signal Strength (Unitless)'].values.tolist())
                try:
                    analyzer.analyzeScan(sweepData, False)
                except AnalysisException as e:
                    print(e)
                finally:
                    if not setZeroPoint:
                        currentTimePoint = readerFileManager.scanNumber - 100000
                        if currentTimePoint >= self.equilibrationTime*60:
                            zeroPoint = getZeroPoint(
                                self.equilibrationTime,
                                analyzer.ResultSet.getMaxFrequencySmooth())
                            setZeroPoint = True
                            analyzer.resetRun()
            self.zeroPointMap[readerId] = zeroPoint
            self.resultSetMap[readerId] = analyzer.ResultSet
            readerProgressBar.finish()
        self.padEntriesWithNan(self.resultSetMap)

    def createSummaryAnalyzed(self):
        rowHeaders = ['Time (hours)']
        firstResultSet = next(iter(self.resultSetMap.values()))
        rowData = [firstResultSet.getTime()]
        if not os.path.exists(self.summaryAnalyzedLocation):
            os.mkdir(self.summaryAnalyzedLocation)
        with open(f"{self.summaryAnalyzedLocation}/summaryAnalyzed.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            for readerId, ResultSet in self.resultSetMap.items():
                rowHeaders.append(f'{readerId} SGI')
                readerSGI = frequencyToIndex(
                    self.zeroPointMap[readerId],
                    ResultSet.getMaxFrequencySmooth()
                )
                rowData.append(readerSGI)

                rowHeaders.append(f'{readerId} Magnitude')
                readerSGI = ResultSet.getMaxVoltsSmooth()
                rowData.append(readerSGI)

                rowHeaders.append(f'{readerId} Peak Width')
                peakWidths = ResultSet.getPeakWidthsSmooth()
                rowData.append(peakWidths)
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))

    @staticmethod
    def padEntriesWithNan(input_dict):
        max_length = max(len(v.getTime()) for v in input_dict.values())

        # Pad each list with None to make them all the same length
        for _, value in input_dict.items():
            while len(value.getTime()) < max_length:
                value.time.append(np.nan)
                value.maxFrequencySmooth.append(np.nan)

        return input_dict

    @staticmethod
    def getAllNumberedFiles(inputList):
        numberedFiles = []
        for item in inputList:
            try:
                float(Path(os.path.basename(item)).stem)
                numberedFiles.append(item)
            except:
                # Filename is not a number
                pass
        return numberedFiles

    @staticmethod
    def sortFn(folderDirectory):
        return int(os.path.basename(os.path.dirname(folderDirectory)).replace("Reader ", ""))