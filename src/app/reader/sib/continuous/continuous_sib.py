from src.app.model.sweep_data import SweepData
from src.app.reader.sib.base_sib import BaseSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib_utils import (
    calculateFrequencyValues,
    removeInitialSpike,
)
from src.resources.sibcontrol.sibcontrol import SIBDDSConfigError, SIBException, SIBConnectionError, SIBTimeoutError


class ContinuousSib(BaseSib):
    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        super().__init__(port, calibrationFileName, readerNumber, portAllocator)

    def takeScan(self, directory: str, currentVolts: float) -> SweepData:
        try:
            self.sib.wake()
            allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
            self.checkAndSendConfiguration()
            allVolts = self.performSweep()
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
        finally:
            self.sib.sleep()
