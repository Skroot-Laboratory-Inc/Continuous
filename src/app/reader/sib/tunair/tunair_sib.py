import logging
import random
import time
from typing import List

import numpy as np

from src.app.custom_exceptions.sib_exception import SIBReconnectException
from src.app.factory.use_case_factory import ContextFactory
from src.app.model.sweep_data import SweepData
from src.app.reader.sib.base_sib import BaseSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib_utils import (
    calculateFrequencyValues,
    removeInitialSpike,
    find_nearest,
    createCalibrationDirectoryIfNotExists,
    createCalibrationFile,
    createReferenceFile,
    convertAdcToVolts,
    getNumPointsSweep,
    normalizeToReference,
)
from src.app.widget import text_notification
from src.app.widget.sidebar.configurations.default_reference_frequency import ReferenceFrequencyConfiguration
from src.app.widget.sidebar.configurations.maximum_reference_voltage import MaximumReferenceVoltageConfiguration
from src.app.widget.sidebar.configurations.minimum_reference_voltage import MinimumReferenceVoltageConfiguration
from src.resources.sibcontrol.sibcontrol import SIBDDSConfigError, SIBException, SIBConnectionError, SIBTimeoutError


class TunairSib(BaseSib):
    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        super().__init__(port, calibrationFileName, readerNumber, portAllocator)

    def _initializeFrequencies(self, Properties):
        """Initialize frequencies from properties and set reference frequency."""
        self.referenceFreqMHz = ReferenceFrequencyConfiguration().getConfig()
        self.stopFreqMHz = Properties.stopFrequency
        self.startFreqMHz = Properties.startFrequency

    def takeScan(self, directory: str, currentVolts: float) -> SweepData:
        try:
            allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
            randomizedFrequency, randomizedVolts = self.performRandomSweep(list(allFrequency), directory)
            return SweepData(randomizedFrequency, randomizedVolts)
        except SIBConnectionError:
            self.resetSibConnection()
            raise SIBConnectionError()
        except SIBTimeoutError:
            self.resetSibConnection()
            raise SIBConnectionError()
        except SIBDDSConfigError:
            self.resetDDSConfiguration()
            raise SIBDDSConfigError()
        except SIBException:
            raise

    def takeCalibrationScan(self) -> bool:
        try:
            self.currentlyScanning.on_next(True)
            createCalibrationDirectoryIfNotExists(self.calibrationFilename)
            startFrequency = self.calibrationStartFreq - self.initialSpikeMhz
            stopFrequency = self.calibrationStopFreq
            numPoints = getNumPointsSweep(startFrequency, stopFrequency)
            allFrequency = calculateFrequencyValues(startFrequency, stopFrequency, self.stepSize)
            self.prepareSweep(startFrequency, stopFrequency, numPoints)
            allVolts = self.performSweep()
            frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
            createCalibrationFile(self.calibrationFilename, frequency, volts)
            return True
        except SIBConnectionError:
            self.resetSibConnection()
            raise SIBConnectionError()
        except SIBTimeoutError:
            self.resetSibConnection()
            raise SIBConnectionError()
        except SIBDDSConfigError:
            self.resetDDSConfiguration()
            raise SIBDDSConfigError()
        except SIBException:
            raise
        finally:
            self.currentlyScanning.on_next(False)

    def setStartFrequency(self, startFreqMHz) -> bool:
        try:
            self.startFreqMHz = startFreqMHz
            self.sib.start_MHz = startFreqMHz
            if self.stopFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            text_notification.setText("Failed to set start frequency.")
            logging.exception(f"Failed to set start frequency. Please check connection on Reader Port {self.readerNumber}.", extra={"id": f"Sib"})
            return False

    def setStopFrequency(self, stopFreqMHz) -> bool:
        try:
            self.stopFreqMHz = stopFreqMHz
            self.sib.stop_MHz = stopFreqMHz
            if self.startFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            text_notification.setText(f"Failed to set stop frequency. Please check connection on Reader Port {self.readerNumber}.")
            logging.exception("Failed to set stop frequency.", extra={"id": f"Sib"})
            return False

    def setReferenceFrequency(self, peakFrequencyMHz: float):
        self.referenceFreqMHz = peakFrequencyMHz - 10

    def prepareSweep(self, startFrequency, stopFrequency, numPoints):
        try:
            self.sib.start_MHz = startFrequency
            self.sib.stop_MHz = stopFrequency
            self.sib.num_pts = numPoints
            self.checkAndSendConfiguration()
        except:
            time.sleep(2)
            self.sib.start_MHz = startFrequency
            self.sib.stop_MHz = stopFrequency
            self.sib.num_pts = numPoints
            self.checkAndSendConfiguration()

    def performSweep(self) -> List[float]:
        self.sib.wake()
        self.sib.write_sweep_command()
        conversion_results, sweep_complete = list(), False
        try:
            while not sweep_complete:
                try:
                    ack_msg, tmp_data = self.sib.read_sweep_response()

                    if ack_msg == 'ok':
                        # SIB has sent the sweep complete command.
                        sweep_complete = True
                    elif ack_msg == 'send_data':
                        # SIB is sending measurement data. Add it to the conversion results array
                        conversion_results.extend(tmp_data)
                    else:
                        logging.info(f"SIB Received an unexpected command. Something is wrong. ack_msg: {ack_msg}", extra={"id": "Sib"})
                except:
                    sweep_complete = True
                    logging.exception("An error occurred while waiting for scan to complete", extra={"id": "Sib"})
                    raise
        except:
            raise
        finally:
            self.sib.sleep()
        return convertAdcToVolts(conversion_results)

    def performRandomSweep(self, frequencyRange: List[float], directory: str) -> (List[float], List[float]):
        shuffledFrequencyRange = random.sample(frequencyRange, len(frequencyRange))
        shuffledVolts = []
        for frequency in shuffledFrequencyRange:
            freq = round(frequency, 1)
            allFreqVolts = []
            allReferenceVolts = []
            averagedFreqVolts = []
            maxReferenceVoltage = MaximumReferenceVoltageConfiguration().getConfig()
            minReferenceVoltage = MinimumReferenceVoltageConfiguration().getConfig()
            if freq > self.referenceFreqMHz:
                stepSize = freq - self.referenceFreqMHz
                self.prepareSweep(self.referenceFreqMHz - stepSize, self.referenceFreqMHz + stepSize, 3)
            elif freq < self.referenceFreqMHz:
                stepSize = abs(freq - self.referenceFreqMHz)
                self.prepareSweep(self.referenceFreqMHz - (2 * stepSize), self.referenceFreqMHz, 3)
            for i in range(ContextFactory().getSibProperties().repeatMeasurements):
                time.sleep(0.005)  # Small delay to allow the DDS to settle
                try:
                    if freq > self.referenceFreqMHz:
                        sweepVolts = self.performSweep()
                        referenceVolts = self.calibrationPointComparison(self.referenceFreqMHz, sweepVolts[1])
                        pointVolts = self.calibrationPointComparison(freq, sweepVolts[2])
                        freqVolts = normalizeToReference(pointVolts, referenceVolts)
                    elif freq < self.referenceFreqMHz:
                        sweepVolts = self.performSweep()
                        referenceVolts = self.calibrationPointComparison(self.referenceFreqMHz, sweepVolts[2])
                        pointVolts = self.calibrationPointComparison(freq, sweepVolts[1])
                        freqVolts = normalizeToReference(pointVolts, referenceVolts)
                    else:
                        referenceVolts = np.nan
                        freqVolts = 1
                    allReferenceVolts.append(referenceVolts)
                    allFreqVolts.append(freqVolts)
                    if minReferenceVoltage < referenceVolts < maxReferenceVoltage or np.isnan(referenceVolts):
                        averagedFreqVolts.append(freqVolts)
                except SIBException:
                    logging.exception(f"Failed to get point at {freq} MHz", extra={"id": "Sib"})
            shuffledVolts.append(np.mean(averagedFreqVolts))
            if freq % 10 == 0 or 9.7 < freq - self.referenceFreqMHz < 10.3:
                createReferenceFile(f"{directory}/{freq} Reference Scan.csv", allReferenceVolts, allFreqVolts)
        sorted_pairs = sorted(zip(shuffledFrequencyRange, shuffledVolts))
        sortedFrequencies, sortedVolts = zip(*sorted_pairs)
        return list(sortedFrequencies), list(sortedVolts)

    def calibrationPointComparison(self, frequency: float, volts: float):
        calibrationVoltsOffset = find_nearest(frequency, self.calibrationFrequency, self.calibrationVolts)
        return volts / calibrationVoltsOffset
