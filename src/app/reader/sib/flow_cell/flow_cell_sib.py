import logging
import time
from typing import List

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
    convertAdcToVolts,
    getNumPointsSweep,
)
from src.app.widget import text_notification
from src.resources.sibcontrol.sibcontrol import SIBDDSConfigError, SIBException, SIBConnectionError, SIBTimeoutError


class FlowCellSib(BaseSib):
    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        super().__init__(port, calibrationFileName, readerNumber, portAllocator)

    def takeScan(self, directory: str, currentVolts: float) -> SweepData:
        try:
            allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
            allVolts = self.performSweepAndWaitForComplete()
            frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
            calibratedVolts = self.calibrationComparison(frequency, volts)
            return SweepData(frequency, calibratedVolts)
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
            self.sib.start_MHz = self.calibrationStartFreq - self.initialSpikeMhz
            self.sib.stop_MHz = self.calibrationStopFreq
            self.sib.num_pts = getNumPointsSweep(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq)
            allFrequency = calculateFrequencyValues(self.calibrationStartFreq - self.initialSpikeMhz, self.calibrationStopFreq, self.stepSize)
            allVolts = self.performSweepAndWaitForComplete()
            frequency, volts = removeInitialSpike(allFrequency, allVolts, self.initialSpikeMhz, self.stepSize)
            createCalibrationFile(self.calibrationFilename, frequency, volts)
            self.setStartFrequency(ContextFactory().getSibProperties().startFrequency)
            self.setStopFrequency(ContextFactory().getSibProperties().stopFrequency)
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
            self.startFreqMHz = startFreqMHz - self.initialSpikeMhz
            self.sib.start_MHz = startFreqMHz - self.initialSpikeMhz
            if self.stopFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            text_notification.setText("Reader hardware disconnected.\nPlease contact your system administrator.")
            logging.exception("Failed to set start frequency.", extra={"id": f"Sib"})
            return False

    def setStopFrequency(self, stopFreqMHz) -> bool:
        try:
            self.stopFreqMHz = stopFreqMHz
            self.sib.stop_MHz = stopFreqMHz
            if self.startFreqMHz:
                self.setNumberOfPoints()
            return True
        except:
            text_notification.setText("Reader hardware disconnected.\nPlease contact your system administrator.")
            logging.exception("Failed to set stop frequency.", extra={"id": f"Sib"})
            return False

    def setReferenceFrequency(self, peakFrequencyMHz: float):
        pass

    def performSweepAndWaitForComplete(self) -> List[str]:
        self.sib.wake()
        self.checkAndSendConfiguration()
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

    def calibrationComparison(self, frequency, volts):
        calibratedVolts = []
        for i in range(len(frequency)):
            calibrationVoltsOffset = find_nearest(frequency[i], self.calibrationFrequency,
                                                  self.calibrationVolts)
            calibratedVolts.append((volts[i] / calibrationVoltsOffset))
        return calibratedVolts
