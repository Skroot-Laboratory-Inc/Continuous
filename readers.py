import json
import os
import shutil

import logger
import text_notification
from algorithms import ContaminationAlgorithm, FoamingAlgorithm, HarvestAlgorithm
from analysis import Analysis
from dev import ReaderDevMode
from emailer import Emailer
from plotting import Plotting


class Reader(Plotting, ContaminationAlgorithm, HarvestAlgorithm):
    def __init__(self, AppModule, readerNumber, outerFrame, totalNumberOfReaders, nPoints, startFreq, stopFreq,
                 scanRate, savePath, readerColor, Vna):
        self.scanMagnitude = []
        self.scanFrequency = []
        self.scanNumber = 100001
        self.folderSuffix = "_Cell"
        self.jsonTextLocation = "serverInfo.json"
        self.waterShift = None
        self.calFileLocation = f'{AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv'
        self.readerName = f"Reader {readerNumber}"
        self.Emailer = Emailer('', f'{self.readerName}')
        self.Emailer.setMessageHarvestClose()
        self.AppModule = AppModule
        self.readerNumber = readerNumber
        self.totalNumberOfReaders = totalNumberOfReaders
        self.nPoints = nPoints
        self.scanRate = scanRate
        self.startFreq = startFreq
        self.stopFreq = stopFreq
        self.Vna = Vna
        self.Vna = Vna
        self.initializeReaderFolders(savePath)
        self.ReaderDevMode = ReaderDevMode(AppModule, readerNumber)
        Plotting.__init__(self, readerColor, outerFrame, readerNumber, AppModule, self.AppModule.secondAxisTitle)
        Analysis.__init__(self, savePath, 51, 101)
        ContaminationAlgorithm.__init__(self, outerFrame, AppModule, self.Emailer, readerNumber)
        HarvestAlgorithm.__init__(self, outerFrame, AppModule, self.Emailer)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)
        self.createServerJsonFile()

    def sendFilesToServer(self):
        self.sendToServer(f'{self.savePath}/{self.scanNumber}.csv')
        self.sendToServer(f'{self.savePath}/Analyzed.csv')
        self.sendToServer(f'{self.savePath}/smoothAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/denoisedAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/splineAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/noFitAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/secondAxis.csv')
        self.sendToServer(f'{os.path.dirname(self.savePath)}/Summary.pdf')
        self.sendToServer(f'{self.savePath}/{self.jsonTextLocation}')

    def addToPdf(self, pdf, currentX, currentY, labelWidth, labelHeight, plotWidth, plotHeight, notesWidth, paddingY):
        pdf.placeText(f"Reader {self.readerNumber}", currentX, currentY, labelWidth, labelHeight, 16, True)
        currentY += labelHeight
        pdf.placePlot(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg', currentX, currentY, plotWidth,
                      plotHeight)
        currentX += plotWidth
        currentY -= (7 * plotHeight) / 8
        currentX -= notesWidth
        currentY -= paddingY
        if self.harvested == False:
            pdf.drawCircle(currentX, currentY, 0.02, 'green')
        else:
            pdf.drawCircle(currentX, currentY, 0.02, 'red')
        currentY += (7 * plotHeight) / 8
        currentX += notesWidth
        currentY += paddingY
        return currentX, currentY

    def updateEmailReceiver(self, receiver_email):
        self.Emailer.changeReceiver(receiver_email)

    def sendToServer(self, filename):
        if not self.AppModule.ServerFileShare.disabled:
            try:
                if os.path.exists(filename):
                    shutil.copy(filename, self.serverSavePath)
            except Exception:
                logger.exception('Failed to send file to server')
        else:
            pass

    def printScanFreq(self):
        text_notification.setText(f"Reader {self.readerNumber} \nFreq: {round(self.minFrequencySmooth[-1], 3)} MHz",
                                  ('Courier', 9, 'bold'), self.AppModule.royalBlue, self.AppModule.white)

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
        self.savePath = rf'{savePath}/{self.readerNumber}{self.folderSuffix}'
        if not self.AppModule.ServerFileShare.disabled:
            self.serverSavePath = rf'{self.AppModule.ServerFileShare.serverLocation}/{self.readerNumber}{self.folderSuffix}'
        else:
            self.serverSavePath = 'incorrect/path'
        self.createFolders()

    def createFolders(self):
        if not os.path.exists(self.serverSavePath) and not self.AppModule.ServerFileShare.disabled:
            os.mkdir(self.serverSavePath)
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)
        if not os.path.exists(f'{self.savePath}/Calibration.csv'):
            if os.path.exists(self.calFileLocation):
                shutil.copy(self.calFileLocation, f'{self.savePath}/Calibration.csv')
            else:
                text_notification.setText(f"No calibration found for \n Reader {self.readerNumber}",
                                          ('Courier', 12, 'bold'), self.AppModule.royalBlue, 'red')
                logger.info(f"No calibration found for Reader {self.readerNumber}")

    # no ops
    def checkFoaming(self):
        pass


class FoamingReader(Reader, FoamingAlgorithm):
    def __init__(self, AppModule, readerNumber, airFreq, waterFreq, waterShift, outerFrame, totalNumberOfReaders,
                 nPoints, startFreq, stopFreq, scanRate, savePath, readerColor, Vna):
        self.scanMagnitude = []
        self.scanFrequency = []
        self.scanNumber = 100001
        self.folderSuffix = "_Foaming"
        self.backgroundColor = '#FFFFFF'
        self.waterShift = waterShift
        self.airFreq = airFreq
        self.waterFreq = waterFreq
        self.nPoints = nPoints
        self.scanRate = scanRate
        self.startFreq = startFreq
        self.stopFreq = stopFreq
        self.calFileLocation = f'{AppModule.desktop}/Calibration/{readerNumber}/Calibration.csv'
        self.Emailer = Emailer('', f'Foaming Reader {readerNumber}')
        self.Emailer.setMessageFoam()
        self.AppModule = AppModule
        self.Vna = Vna
        self.Vna = Vna
        self.readerNumber = readerNumber
        self.totalNumberOfReaders = totalNumberOfReaders
        self.initializeReaderFolders(savePath)
        Plotting.__init__(self, readerColor, outerFrame, readerNumber, AppModule)
        Analysis.__init__(self, savePath, 11, 21)
        FoamingAlgorithm.__init__(self, airFreq, waterFreq, waterShift, AppModule, self.Emailer)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)

    def sendFilesToServer(self):
        self.sendToServer(f'{self.savePath}/{self.scanNumber}.csv')
        self.sendToServer(f'{self.savePath}/Analyzed.csv')
        self.sendToServer(f'{self.savePath}/smoothAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/denoisedAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/splineAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/noFitAnalyzed.csv')
        self.sendToServer(f'{self.savePath}/secondAxis.csv')
        self.sendToServer(f'{os.path.dirname(self.savePath)}/Summary.pdf')

    def addToPdf(self, pdf, currentX, currentY, labelWidth, labelHeight, plotWidth, plotHeight, notesWidth, paddingY):
        pdf.placeText(f"Reader {self.readerNumber}", currentX, currentY, labelWidth, labelHeight, 16, True)
        currentY += labelHeight
        pdf.placePlot(f'{os.path.dirname(self.savePath)}/Reader {self.readerNumber}.jpg', currentX, currentY, plotWidth,
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
