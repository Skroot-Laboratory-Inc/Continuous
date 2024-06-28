import json
import logging
import os
import shutil
import socket

import paramiko
from scp import SCPClient

from src.app.algorithm.algorithms import ContaminationAlgorithm, HarvestAlgorithm
from src.app.aws.aws import AwsBoto3
from src.app.helper.helper_functions import getOperatingSystem
from src.app.initialization.dev import ReaderDevMode
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.reader.analysis import Analysis
from src.app.reader.plotting import Plotting
from src.app.sib.reader_interface import ReaderInterface
from src.app.widget import text_notification


class Reader(ContaminationAlgorithm, HarvestAlgorithm, ReaderDevMode):
    def __init__(self, AppModule, readerNumber, outerFrame, totalNumberOfReaders, startFreq, stopFreq,
                 scanRate, savePath, readerColor, ReaderInterface: ReaderInterface):
        self.FileManager = ReaderFileManager(savePath, readerNumber)
        self.AppModule = AppModule
        self.readerNumber = readerNumber
        self.totalNumberOfReaders = totalNumberOfReaders
        self.initializeReaderFolders(savePath)
        if not self.AppModule.DevMode.isDevMode:
            ReaderInterface.setStartFrequency(startFreq)
            ReaderInterface.setStopFrequency(stopFreq)
        self.ReaderInterface = ReaderInterface
        if not AppModule.DevMode.isDevMode:
            self.yAxisLabel = ReaderInterface.yAxisLabel
        else:
            self.yAxisLabel = "Signal Strength (Unitless)"
        self.sshDisabled = False
        self.Aws = AwsBoto3()
        self.scp = None
        self.sshConnection = None
        self.scanMagnitude = []
        self.scanFrequency = []
        self.scanRate = scanRate
        Plotting.__init__(self, readerColor, outerFrame, readerNumber, AppModule, self.FileManager, self.AppModule.secondAxisTitle)
        Analysis.__init__(self, self.FileManager)
        ReaderDevMode.__init__(self, AppModule, readerNumber)
        ContaminationAlgorithm.__init__(self, outerFrame, AppModule, readerNumber)
        HarvestAlgorithm.__init__(self, outerFrame, AppModule)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)
        self.createServerJsonFile()
        self.AppModule.freqToggleSet.subscribe(lambda toggle: self.setToggle(toggle))

    def sendFilesToServer(self):
        try:
            all_files = [
                self.FileManager.getCurrentScan(),
                self.FileManager.getAnalyzed(),
                self.FileManager.getSmoothAnalyzed(),
                self.FileManager.getSecondAxis(),
                self.FileManager.getSummaryPdf(),
                self.FileManager.getServerInfo(),
            ]

            files_to_send = []
            for file in all_files:
                if os.path.exists(file):
                    files_to_send.append(file)
            operatingSystem = getOperatingSystem()
            if operatingSystem == "windows":
                for file in files_to_send:
                    self.sendToServer(file)
            elif operatingSystem == "linux" and not self.sshDisabled:
                self.scp.put(files_to_send, self.serverSavePath)
        except:
            logging.exception("Failed to send files to server")

    def addToPdf(self, pdf, currentX, currentY, labelWidth, plotWidth, plotHeight, notesWidth, paddingY):
        pdf.placeImage(self.FileManager.getReaderPlotJpg(), currentX, currentY, plotWidth, plotHeight)
        currentX += plotWidth
        if not self.harvested:
            pdf.drawCircle(currentX, currentY, 0.02, 'green')
        else:
            pdf.drawCircle(currentX, currentY, 0.02, 'red')
        return currentX, currentY

    def sendToServer(self, filename):
        if not self.AppModule.ServerFileShare.disabled:
            try:
                if os.path.exists(filename):
                    shutil.copy(filename, self.serverSavePath)
            except Exception:
                logging.exception('Failed to send file to server')
        else:
            pass

    def createServerJsonFile(self):
        dictionary = {
            "backgroundColor": self.backgroundColor,
            "indicatorColor": self.indicatorColor,
        }
        json_object = json.dumps(dictionary, indent=4)
        with open(self.FileManager.getServerInfo(), 'w') as f:
            f.write(json_object)

    def initializeReaderFolders(self, savePath):
        self.setSavePath(savePath)

    def setSavePath(self, savePath):
        if not os.path.exists(savePath):
            os.mkdir(savePath)
        operatingSystem = getOperatingSystem()
        if operatingSystem == "windows":
            if not self.AppModule.ServerFileShare.disabled:
                self.serverSavePath = rf'{self.AppModule.ServerFileShare.serverLocation}/Reader {self.readerNumber}'
            else:
                self.serverSavePath = 'incorrect/path'
        if operatingSystem == "linux":
            try:
                aws_secret = self.Aws.getSshSecret()
                if aws_secret is None or self.sshDisabled:
                    logging.exception("Failure to find aws secret")
                else:
                    self.initializeSSHConnection(
                        aws_secret["host"], aws_secret["port"], aws_secret["username"], aws_secret["password"]
                    )
            except:
                self.sshDisabled = True
            if not self.sshDisabled:
                self.serverSavePath = f'D:/data/{socket.gethostname()}/Reader {self.readerNumber}'
                serverSavePath_ = self.serverSavePath.replace('/', '\\')
                stdin_, stdout_, stderr_ = self.sshConnection.exec_command(rf"md {serverSavePath_}")
                stdout, stderr = stdout_.read(), stderr_.read()
                if stderr != b'':
                    logging.exception(f"Could not create folder after connecting to the server: {stderr}")
        self.createFolders()

    def initializeSSHConnection(self, hostname, port, username, password):
        try:
            self.sshConnection = paramiko.SSHClient()
            self.sshConnection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshConnection.connect(
                hostname=hostname, port=port,
                username=username, password=password,
                timeout=5)
            self.scp = SCPClient(self.sshConnection.get_transport())
            logging.info(f"Connection Established with {username}@{hostname}:{port}")
        except:
            self.sshDisabled = True
            logging.exception("There was an error SSH connecting to the server")

    def createFolders(self):
        if getOperatingSystem() == "windows" and not os.path.exists(
                self.serverSavePath) and not self.AppModule.ServerFileShare.disabled:
            os.mkdir(self.serverSavePath)
        if not os.path.exists(self.FileManager.getReaderSavePath()):
            os.mkdir(self.FileManager.getReaderSavePath())
        if not os.path.exists(self.FileManager.getCalibrationLocalLocation()):
            if os.path.exists(self.FileManager.getCalibrationGlobalLocation()):
                shutil.copy(self.FileManager.getCalibrationGlobalLocation(), self.FileManager.getCalibrationLocalLocation())
            else:
                text_notification.setText(f"No calibration found for \n Reader {self.readerNumber}",
                                          ('Courier', 12, 'bold'), self.AppModule.primaryColor, 'red')
                logging.info(f"No calibration found for Reader {self.readerNumber}")

    def resetReaderRun(self):
        self.time = self.time[-1:]
        self.timestamp = self.timestamp[-1:]
        self.filenames = self.filenames[-1:]
        self.denoiseTime = self.denoiseTime[-1:]
        self.denoiseTimeSmooth = self.denoiseTimeSmooth[-1:]
        self.maxFrequency = self.maxFrequency[-1:]
        self.maxFrequencySmooth = self.maxFrequencySmooth[-1:]
        self.denoiseFrequency = self.denoiseFrequency[-1:]
        self.denoiseFrequencySmooth = self.denoiseFrequencySmooth[-1:]
        self.maxVoltsSmooth = self.maxVoltsSmooth[-1:]

