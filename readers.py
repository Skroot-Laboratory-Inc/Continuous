import json
import os
import shutil
from statistics import mean

import logger
import text_notification
from algorithms import ContaminationAlgorithm, FoamingAlgorithm, HarvestAlgorithm
from analysis import Analysis
from dac import Dac
from dev import ReaderDevMode
from emailer import Emailer
from indicator import Indicator
from initialization import Initialization
from notes import ExperimentNotes
from plotting import Plotting, SecondAxis
from vna import VnaScanning


class Reader(Analysis, ReaderDevMode, Initialization, Plotting, Indicator,
             ContaminationAlgorithm, HarvestAlgorithm, ExperimentNotes, SecondAxis):
    def __init__(self, AppModule, readerNumber, outerFrame, totalNumberOfReaders, nPoints, startFreq, stopFreq,
                 scanRate, savePath, readerColor, Vna):
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
        self.initializeDefaults(savePath, outerFrame, readerColor)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)
        self.initializeContamination(outerFrame)
        self.initializeHarvest(outerFrame)
        self.createServerJsonFile()

    def determineFitPoints(self):
        minMag = abs(min(self.scanMagnitude))
        meanMag = abs(mean(self.scanMagnitude))
        if (minMag - meanMag) < 1:
            return 51
        elif (minMag - meanMag) > 1:
            return 101

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
        if self.AppModule.ServerFileShare.disabled == False:
            try:
                if os.path.exists(filename):
                    shutil.copy(filename, self.serverSavePath)
            except Exception as e:
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

    # no ops
    def checkFoaming(self):
        pass


class FoamingReader(Reader, FoamingAlgorithm):
    def __init__(self, AppModule, readerNumber, airFreq, waterFreq, waterShift, outerFrame, totalNumberOfReaders,
                 nPoints, startFreq, stopFreq, scanRate, savePath, readerColor, Vna):
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
        self.Dac = Dac()
        self.readerNumber = readerNumber
        self.totalNumberOfReaders = totalNumberOfReaders
        self.initializeDefaults(savePath, outerFrame, readerColor)
        self.createFrequencyFrame(outerFrame, totalNumberOfReaders)

    def determineFitPoints(self):
        minMag = abs(min(self.scanMagnitude))
        meanMag = abs(mean(self.scanMagnitude))
        if (minMag - meanMag) < 1:
            return 11
        elif (minMag - meanMag) > 1:
            return 21

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
