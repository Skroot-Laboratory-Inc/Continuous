import numpy as np

from src.app.custom_exceptions.analysis_exception import SensorNotFoundException
from src.app.model.sweep_data import SweepData
from src.app.reader.sib.base_sib import BaseSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.roller_bottle.vna_sweep_optimizer import VnaSweepOptimizer
from src.resources.sibcontrol.sibcontrol import SIBDDSConfigError, SIBException, SIBConnectionError, SIBTimeoutError


class RollerBottleSib(BaseSib):
    def __init__(self, port, calibrationFileName, readerNumber, portAllocator: PortAllocator):
        super().__init__(port, calibrationFileName, readerNumber, portAllocator)

    def takeScan(self, directory: str, currentVolts: float) -> SweepData:
        try:
            self.sib.wake()
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
        finally:
            self.sib.sleep()
