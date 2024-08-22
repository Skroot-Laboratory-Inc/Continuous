import os
import shutil

from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.file_manager.global_file_manager import GlobalFileManager


class EndExperimentFileCopier:
    def __init__(self, globalFileManager: GlobalFileManager):
        self.GlobalFileManager = globalFileManager
        self.CommonFileManager = CommonFileManager()
        pass

    def copyFilesToDebuggingFolder(self, Readers):
        logSubdir = f'{self.GlobalFileManager.getSavePath()}/Log'
        if not os.path.exists(logSubdir):
            os.mkdir(logSubdir)
        filesToCopy = {self.CommonFileManager.getExperimentLog(): 'Experiment Log.txt'}
        for Reader in Readers:
            filesToCopy[
                Reader.FileManager.getCalibrationLocalLocation()
            ] = f'Calibration_{Reader.readerNumber}.csv'
        for currentFileLocation, newFileLocation in filesToCopy.items():
            if os.path.exists(currentFileLocation):
                shutil.copy(currentFileLocation, f'{logSubdir}/{newFileLocation}')

    def copyFilesToAnalysisFolder(self, Readers):
        analysisSubdir = f'{self.GlobalFileManager.getSavePath()}/Analysis'
        if not os.path.exists(analysisSubdir):
            os.mkdir(analysisSubdir)
        filesToCopy = {
            self.GlobalFileManager.getSummaryAnalyzed(): 'Experiment Summary.csv',
            self.GlobalFileManager.getSummaryPdf(): 'Experiment Summary.pdf',
            self.GlobalFileManager.getExperimentNotesTxt(): 'Experiment Notes.txt',
            self.GlobalFileManager.getSetupForm(): 'Setup Form.png',
            self.CommonFileManager.getReadme(): 'README.md',
        }
        for Reader in Readers:
            filesToCopy[Reader.FileManager.getSecondAxis()] = f'Reader {Reader.readerNumber} Second Axis.csv'
        for currentFileLocation, newFileLocation in filesToCopy.items():
            if os.path.exists(currentFileLocation):
                shutil.copy(currentFileLocation, f'{analysisSubdir}/{newFileLocation}')

