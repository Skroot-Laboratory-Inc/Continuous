import logging
import random
import time
from typing import List

import numpy as np

from src.app.factory.use_case_factory import ContextFactory
from src.app.model.sweep_data import SweepData
from src.app.reader.sib.base_sib import BaseSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib_utils import (
    calculateFrequencyValues,
    createReferenceFile,
    normalizeToReference,
)
from src.app.widget.sidebar.configurations.default_reference_frequency import ReferenceFrequencyConfiguration
from src.app.widget.sidebar.configurations.maximum_reference_voltage import MaximumReferenceVoltageConfiguration
from src.app.widget.sidebar.configurations.minimum_reference_voltage import MinimumReferenceVoltageConfiguration
from src.resources.sibcontrol.sibcontrol import SIBDDSConfigError, SIBException, SIBConnectionError, SIBTimeoutError


class TunairSib(BaseSib):
    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        super().__init__(port, calibrationFileName, readerNumber, portAllocator)
        self.referenceFreqMHz = ReferenceFrequencyConfiguration().getConfig()

    def setReferenceFrequency(self, peakFrequencyMHz: float):
        self.referenceFreqMHz = peakFrequencyMHz - 10

    def takeScan(self, directory: str, currentVolts: float) -> SweepData:
        try:
            self.sib.wake()
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
        finally:
            self.sib.sleep()

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
