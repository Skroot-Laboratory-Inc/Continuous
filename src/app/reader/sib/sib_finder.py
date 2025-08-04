import logging
import os

from src.app.helper_methods.helper_functions import getSibPort
from src.app.properties.dev_properties import DevProperties
from src.app.reader.sib.dev_sib import DevSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib import Sib
from src.app.reader.sib.sib_interface import SibInterface
from src.app.widget import text_notification


class SibFinder:
    def __init__(self):
        self.PortAllocator = PortAllocator()

    def connectSib(self, readerNumber: int, calibrationRequired):
        if not DevProperties().isDevMode:
            port = self.PortAllocator.getPortForReader(readerNumber)
            return instantiateReader(port, self.PortAllocator, calibrationRequired, readerNumber)
        else:
            return DevSib(readerNumber)


def instantiateReader(port, portAllocator, calibrationRequired, readerNumber) -> SibInterface:
    try:
        sib = Sib(
            port,
            getReaderCalibrationFile(),
            readerNumber,
            portAllocator,
            calibrationRequired,
        )
        success = sib.performHandshake()
        if success:
            text_notification.setText("SIB connection successful.")
            return sib
        else:
            logging.info(f"Failed to handshake SIB  on port {port}", extra={"id": "Sib"})
            text_notification.setText("Failed to connect to SiB")
            portAllocator.removePort(port)
            sib.close()
    except:
        logging.exception(f"Failed to instantiate reader.", extra={"id": "Sib"})


def getDesktopLocation():
    """ This gets the path to the computer's desktop. """
    try:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except KeyError:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')


def getReaderCalibrationFile() -> str:
    return f'{getDesktopLocation()}/Backend/Calibration/1/Calibration.csv'
