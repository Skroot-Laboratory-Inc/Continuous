import logging
import os

from src.app.properties.dev_properties import DevProperties
from src.app.reader.sib.continuous.continuous_sib import ContinuousSib
from src.app.reader.sib.dev_sib import DevSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.flow_cell.flow_cell_sib import FlowCellSib
from src.app.reader.sib.roller_bottle.roller_bottle_sib import RollerBottleSib
from src.app.reader.sib.sib_interface import SibInterface
from src.app.reader.sib.tunair.tunair_sib import TunairSib
from src.app.widget import text_notification
from src.resources.version.version import Version, UseCase


class SibFinder:
    def __init__(self):
        self.PortAllocator = PortAllocator()

    def connectSib(self, readerNumber: int):
        if not DevProperties().isDevMode:
            port = self.PortAllocator.getPortForReader(readerNumber)
            return instantiateReader(port, self.PortAllocator, readerNumber)
        else:
            return DevSib(readerNumber)


def instantiateReader(port, portAllocator, readerNumber) -> SibInterface:
    try:
        # TODO Use context provider or factory pattern here to provide the Sib type based on UseCase
        if Version().useCase == UseCase.FlowCell:
            sib = FlowCellSib(
                port,
                getReaderCalibrationFile(),
                readerNumber,
                portAllocator,
            )
        elif Version().useCase == UseCase.RollerBottle:
            sib = RollerBottleSib(
                port,
                getReaderCalibrationFile(),
                readerNumber,
                portAllocator,
            )
        elif Version().useCase == UseCase.Manufacturing:
            sib = ContinuousSib(
                port,
                getReaderCalibrationFile(),
                readerNumber,
                portAllocator,
            )
        elif Version().useCase == UseCase.Tunair:
            sib = TunairSib(
                port,
                getReaderCalibrationFile(),
                readerNumber,
                portAllocator,
            )
        else:
            raise Exception("Unsupported use case for SIB instantiation.")
        success = sib.performHandshake()
        if success:
            text_notification.setText("Reader hardware connected successfully.")
            return sib
        else:
            logging.info(f"Failed to handshake SIB  on port {port}", extra={"id": "Sib"})
            text_notification.setText("Reader hardware disconnected.\nPlease contact your system administrator.")
            portAllocator.removePort(port)
            sib.close()
    except:
        logging.exception(f"Failed to connect to reader hardware.", extra={"id": "Sib"})


def getDesktopLocation():
    """ This gets the path to the computer's desktop. """
    try:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except KeyError:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')


def getReaderCalibrationFile() -> str:
    return f'{getDesktopLocation()}/Backend/Calibration/1/Calibration.csv'
