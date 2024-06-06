import json
import logging
import os
import shutil
import socket

import paramiko
from scp import SCPClient

import text_notification
from algorithms import ContaminationAlgorithm, FoamingAlgorithm, HarvestAlgorithm
from analysis import Analysis
from aws import AwsBoto3
from dev import ReaderDevMode
from emailer import Emailer
from plotting import Plotting
from reader_interface import ReaderInterface


class Reader(ContaminationAlgorithm, HarvestAlgorithm, ReaderDevMode):
    def __init__(self, AppModule, readerNumber, outerFrame, totalNumberOfReaders, startFreq, stopFreq,
                 scanRate, savePath, readerColor, ReaderInterface: ReaderInterface):
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
        self.scanNumber = 100001
        self.jsonTextLocation = "serverInfo.json"
        self.waterShift = None
        self.calFileLocation = f'{AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv'
        self.readerName = f"Reader {readerNumber}"
        self.Emailer = Emailer('', f'{self.readerName}')
        self.Emailer.setMessageHarvestClose()
        self.AppModule = AppModule
        self.readerNumber = readerNumber
        self.totalNumberOfReaders = totalNumberOfReaders
        self.scanRate = scanRate
        if self.AppModule.DevMode.isDevMode == False:
            ReaderInterface.setStartFrequency(startFreq)
            ReaderInterface.setStopFrequency(stopFreq)
        self.ReaderInterface = ReaderInterface
        self.initializeReaderFolders(savePath)
        Plotting.__init__(self, readerColor, outerFrame, readerNumber, AppModule, self.AppModule.secondAxisTitle)
        Analysis.__init__(self, self.savePath, 41, 61)
        ReaderDevMode.__init__(self, AppModule, readerNumber)
        ContaminationAlgorithm.__init__(self, outerFrame, AppModule, self.Emailer, readerNumber)
        HarvestAlgorithm.__init__(self, outerFrame, AppModule, self.Emailer)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)
        self.createServerJsonFile()
        self.AppModule.freqToggleSet.subscribe(lambda toggle: self.setToggle(toggle))

    def sendFilesToServer(self):
        try:
            all_files = [
                f'{self.savePath}/{self.scanNumber}.csv',
                f'{self.savePath}/Analyzed.csv',
                f'{self.savePath}/smoothAnalyzed.csv',
                f'{self.savePath}/secondAxis.csv',
                f'{os.path.dirname(self.savePath)}/Summary.pdf',
                f'{self.savePath}/{self.jsonTextLocation}',
            ]

            files_to_send = []
            for file in all_files:
                if os.path.exists(file):
                    files_to_send.append(file)

            if self.AppModule.os == "windows":
                for file in files_to_send:
                    self.sendToServer(file)
            elif self.AppModule.os == "linux" and not self.sshDisabled:
                self.scp.put(files_to_send, self.serverSavePath)
        except:
            logging.exception("Failed to send files to server")

    def addToPdf(self, pdf, currentX, currentY, labelWidth, plotWidth, plotHeight, notesWidth, paddingY):
        pdf.placeImage(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg', currentX, currentY,
                       plotWidth,
                       plotHeight)
        currentX += plotWidth
        if not self.harvested:
            pdf.drawCircle(currentX, currentY, 0.02, 'green')
        else:
            pdf.drawCircle(currentX, currentY, 0.02, 'red')
        return currentX, currentY

    def updateEmailReceiver(self, receiver_email):
        self.Emailer.changeReceiver(receiver_email)

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
        with open(f'{self.savePath}/{self.jsonTextLocation}', 'w') as f:
            f.write(json_object)

    def initializeReaderFolders(self, savePath):
        self.setSavePath(savePath)

    def setSavePath(self, savePath):
        if not os.path.exists(savePath):
            os.mkdir(savePath)
        self.savePath = rf'{savePath}/Reader {self.readerNumber}'
        if self.AppModule.os == "windows":
            if not self.AppModule.ServerFileShare.disabled:
                self.serverSavePath = rf'{self.AppModule.ServerFileShare.serverLocation}/Reader {self.readerNumber}'
            else:
                self.serverSavePath = 'incorrect/path'
        if self.AppModule.os == "linux":
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
        if self.AppModule.os == "windows" and not os.path.exists(
                self.serverSavePath) and not self.AppModule.ServerFileShare.disabled:
            os.mkdir(self.serverSavePath)
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)
        if not os.path.exists(f'{self.savePath}/Calibration.csv'):
            if os.path.exists(self.calFileLocation):
                shutil.copy(self.calFileLocation, f'{self.savePath}/Calibration.csv')
            else:
                text_notification.setText(f"No calibration found for \n Reader {self.readerNumber}",
                                          ('Courier', 12, 'bold'), self.AppModule.royalBlue, 'red')
                logging.info(f"No calibration found for Reader {self.readerNumber}")

    def resetReaderRun(self):
        self.time = self.time[-1:]
        self.timestamp = self.timestamp[-1:]
        self.filenames = self.filenames[-1:]
        self.denoiseTime = self.denoiseTime[-1:]
        self.denoiseTimeSmooth = self.denoiseTimeSmooth[-1:]
        self.minFrequency = self.minFrequency[-1:]
        self.minFrequencySmooth = self.minFrequencySmooth[-1:]
        self.denoiseFrequency = self.denoiseFrequency[-1:]
        self.denoiseFrequencySmooth = self.denoiseFrequencySmooth[-1:]
        self.minDbSmooth = self.minDbSmooth[-1:]

    # no ops
    def checkFoaming(self):
        pass


class FoamingReader(Reader, FoamingAlgorithm, ReaderDevMode):
    def __init__(self, AppModule, readerNumber, airFreq, waterFreq, waterShift, outerFrame, totalNumberOfReaders, startFreq, stopFreq, scanRate, savePath, readerColor, ReaderInterface):
        self.scanMagnitude = []
        self.scanFrequency = []
        self.scanNumber = 100001
        self.backgroundColor = '#FFFFFF'
        self.waterShift = waterShift
        self.airFreq = airFreq
        self.waterFreq = waterFreq
        self.scanRate = scanRate
        self.calFileLocation = f'{AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv'
        self.Emailer = Emailer('', f'Foaming Reader {readerNumber}')
        self.Emailer.setMessageFoam()
        self.AppModule = AppModule
        ReaderInterface.setStartFrequency(startFreq)
        ReaderInterface.setStopFrequency(stopFreq)
        self.ReaderInterface = ReaderInterface
        self.readerNumber = readerNumber
        self.totalNumberOfReaders = totalNumberOfReaders
        self.initializeReaderFolders(savePath)
        Plotting.__init__(self, readerColor, outerFrame, readerNumber, AppModule)
        Analysis.__init__(self, self.savePath, 11, 21)
        FoamingAlgorithm.__init__(self, airFreq, waterFreq, waterShift, AppModule, self.Emailer)
        ReaderDevMode.__init__(self, AppModule, readerNumber)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)

    def sendFilesToServer(self):
        self.sendToServer(f'{self.savePath}/{self.scanNumber}.csv')
        self.sendToServer(f'{self.savePath}/Analyzed.csv')
        self.sendToServer(f'{self.savePath}/smoothAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/secondAxis.csv')
        self.sendToServer(f'{os.path.dirname(self.savePath)}/Summary.pdf')
        self.sendToServer(f'{os.path.dirname(self.savePath)}/summaryAnalyzed.csv')

    def addToPdf(self, pdf, currentX, currentY, labelWidth, plotWidth, plotHeight, notesWidth, paddingY):
        pdf.placeImage(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg', currentX, currentY,
                       plotWidth,
                       plotHeight)
        currentX += plotWidth
        return currentX, currentY

    # no ops
    def createServerJsonFile(self):
        pass

    def checkContamination(self):
        pass

    def checkHarvest(self):
        pass

    def addInoculationMenuBar(self, menu):
        pass
