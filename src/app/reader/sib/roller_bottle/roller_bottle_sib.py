import logging
import time
from typing import List

import numpy as np

from src.app.custom_exceptions.analysis_exception import SensorNotFoundException
from src.app.custom_exceptions.sib_exception import SIBReconnectException
from src.app.factory.use_case_factory import ContextFactory
from src.app.model.sweep_data import SweepData
from src.app.reader.sib.base_sib import BaseSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.roller_bottle.vna_sweep_optimizer import VnaSweepOptimizer
from src.app.reader.sib.sib_utils import (
    calculateFrequencyValues,
    removeInitialSpike,
    find_nearest,
    createCalibrationDirectoryIfNotExists,
    createCalibrationFile,
    convertAdcToVolts,
    getNumPointsSweep,
)
from src.app.widget import text_notification
from src.app.widget.sidebar.configurations.default_reference_frequency import ReferenceFrequencyConfiguration
from src.resources.sibcontrol.sibcontrol import SIBDDSConfigError, SIBException, SIBConnectionError, SIBTimeoutError


class RollerBottleSib(BaseSib):
    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        super().__init__(port, calibrationFileName, readerNumber, portAllocator)

    def _initializeFrequencies(self, Properties):
        """Initialize frequencies from properties and set reference frequency."""
        self.referenceFreqMHz = ReferenceFrequencyConfiguration().getConfig()
        self.stopFreqMHz = Properties.stopFrequency
        self.startFreqMHz = Properties.startFrequency

    def takeScan(self, directory: str, currentVolts: float) -> SweepData:
        try:
            optimizer = VnaSweepOptimizer(currentVolts) if not np.isnan(currentVolts) else VnaSweepOptimizer()
            sweepData = optimizer.performOptimizedSweep(
                self,
                self.startFreqMHz,
                self.stopFreqMHz,
            )
            return sweepData
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
        except SensorNotFoundException:
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

    def calibrationPointComparison(self, frequency: float, volts: float):
        calibrationVoltsOffset = find_nearest(frequency, self.calibrationFrequency, self.calibrationVolts)
        return volts / calibrationVoltsOffset
