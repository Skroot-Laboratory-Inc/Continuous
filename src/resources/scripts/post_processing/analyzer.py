import csv
import glob
import os
from itertools import zip_longest
from pathlib import Path

import numpy as np
import pandas
from progress.bar import IncrementalBar

from src.app.helper_methods.custom_exceptions.analysis_exception import AnalysisException
from src.app.helper_methods.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper_methods.helper_functions import getZeroPoint
from src.app.helper_methods.model.sweep_data import SweepData
from src.app.reader.algorithm.harvest_algorithm import HarvestAlgorithm
from src.app.reader.analyzer.analyzer import Analyzer


class PostProcessingAnalyzer:
    def __init__(self, experimentFolderDirectory, equilibrationTime):
        self.equilibrationTime = equilibrationTime
        self.experimentFolderDirectory = experimentFolderDirectory
        self.summaryAnalyzedLocation = f'{self.experimentFolderDirectory}/Post Processing'
        self.readerDirectories = self._discoverReaderDirectories(experimentFolderDirectory)
        self.rawDataScansMap = {}
        self.resultSetMap = {}
        self.zeroPointMap = {}

    def getScansForReaders(self):
        for directory in self.readerDirectories:
            allFiles = sorted(glob.glob(f'{directory}/*.csv'))
            rawDataScans = self.getAllNumberedFiles(allFiles)
            readerId = os.path.basename(os.path.dirname(directory + os.sep))
            self.rawDataScansMap[readerId] = rawDataScans

    def analyzeReaderScans(self):
        for readerId, rawDataFiles in self.rawDataScansMap.items():
            if not rawDataFiles:
                continue
            firstTimestamp = int(Path(os.path.basename(rawDataFiles[0])).stem)
            readerFileManager = ReaderFileManager(os.path.dirname(rawDataFiles[0]), 1)
            analyzer = Analyzer(readerFileManager, HarvestAlgorithm(readerFileManager))
            # Seed start time to the first scan so Time (hours) is computed from the experiment, not "now".
            analyzer.ResultSet.startTime = firstTimestamp
            zeroPointSet = False
            zeroPoint = 1
            readerProgressBar = IncrementalBar(
                f'{readerId}',
                suffix='%(percent)d%%',
                max=len(rawDataFiles))
            for file in rawDataFiles:
                readerProgressBar.next()
                readerFileManager.scanDateMillis = int(Path(os.path.basename(file)).stem)
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
                    if not zeroPointSet:
                        elapsedHours = (readerFileManager.scanDateMillis - firstTimestamp) / 3600000
                        if elapsedHours >= self.equilibrationTime:
                            zeroPoint = getZeroPoint(
                                self.equilibrationTime,
                                analyzer.ResultSet.getMaxFrequencySmooth())
                            zeroPointSet = True
                            analyzer.setZeroPoint(zeroPoint)
                            analyzer.resetRun()
            self.zeroPointMap[readerId] = zeroPoint
            self.resultSetMap[readerId] = analyzer.ResultSet
            readerProgressBar.finish()
        self.padEntriesWithNan(self.resultSetMap)

    def createSummaryAnalyzed(self):
        if not self.resultSetMap:
            return
        rowHeaders = ['Time (hours)']
        firstResultSet = next(iter(self.resultSetMap.values()))
        rowData = [firstResultSet.getTime()]
        if not os.path.exists(self.summaryAnalyzedLocation):
            os.mkdir(self.summaryAnalyzedLocation)
        with open(f"{self.summaryAnalyzedLocation}/summaryAnalyzed.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            for readerId, ResultSet in self.resultSetMap.items():
                rowHeaders.append(f'{readerId} SGI')
                readerSGI = self._toSGI(
                    self.zeroPointMap[readerId],
                    ResultSet.getMaxFrequencySmooth()
                )
                rowData.append(readerSGI)

                rowHeaders.append(f'{readerId} Magnitude')
                rowData.append(ResultSet.getMaxVoltsSmooth())

                rowHeaders.append(f'{readerId} Peak Width')
                rowData.append(ResultSet.getPeakWidthsSmooth())
            writer.writerow(rowHeaders)
            writer.writerows(zip_longest(*rowData, fillvalue=np.nan))

    @staticmethod
    def _toSGI(zeroPoint, frequencies):
        """Convert frequency values to SGI %. Independent of dev-mode flags so post-processing
        always produces percent-scale SGI, regardless of how the live Analyzer was configured."""
        return [
            max(0.0, 100.0 * (1.0 - val / zeroPoint)) if not np.isnan(val) else np.nan
            for val in frequencies
        ]

    @staticmethod
    def _discoverReaderDirectories(experimentFolderDirectory):
        """Return list of reader directories. Supports both multi-reader (Reader N subfolders)
        and single-reader (scans directly in the given directory) layouts."""
        readerDirs = [folder for folder in glob.glob(f'{experimentFolderDirectory}/Reader */')]
        if readerDirs:
            readerDirs.sort(key=PostProcessingAnalyzer.sortFn)
            return readerDirs
        return [f"{experimentFolderDirectory}/"]

    @staticmethod
    def padEntriesWithNan(input_dict):
        if not input_dict:
            return input_dict
        max_length = max(len(v.getTime()) for v in input_dict.values())
        for _, value in input_dict.items():
            while len(value.getTime()) < max_length:
                value.time.append(np.nan)
                value.maxFrequencySmooth.append(np.nan)
                value.maxVoltsSmooth.append(np.nan)
                value.peakWidthsSmooth.append(np.nan)
        return input_dict

    @staticmethod
    def getAllNumberedFiles(inputList):
        numberedFiles = []
        for item in inputList:
            try:
                float(Path(os.path.basename(item)).stem)
                numberedFiles.append(item)
            except ValueError:
                pass
        return numberedFiles

    @staticmethod
    def sortFn(folderDirectory):
        return int(os.path.basename(os.path.dirname(folderDirectory)).replace("Reader ", ""))
