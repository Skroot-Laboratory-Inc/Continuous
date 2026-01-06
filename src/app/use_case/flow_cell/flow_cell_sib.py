from src.app.helper_methods.custom_exceptions.sib_exception import CancelSweepException
from src.app.helper_methods.model.sweep_data import SweepData
from src.app.reader.sib.base_sib import BaseSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib_utils import (
    calculateFrequencyValues,
    removeInitialSpike,
)
from src.resources.sibcontrol.sibcontrol import SIBDDSConfigError, SIBException, SIBConnectionError, SIBTimeoutError


class FlowCellSib(BaseSib):
    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        super().__init__(port, calibrationFileName, readerNumber, portAllocator)

    def takeScan(self, directory: str, currentVolts: float, shutdown_flag=None) -> SweepData:
        try:
            self.sib.wake()
            allFrequency = calculateFrequencyValues(self.startFreqMHz, self.stopFreqMHz, self.stepSize)
            self.checkAndSendConfiguration()
            allVolts = self.performSweep(shutdown_flag)
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
        except CancelSweepException:
            self.sib.close()
            self.sib.open()
            self.sib.reset_output_buffer()
            self.sib.reset_input_buffer()
            self.sib.reset_sib()
        except SIBException:
            raise
        finally:
            try:
                self.sib.sleep()
            except:
                pass
