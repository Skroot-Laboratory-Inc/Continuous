import logging
import os

from src.app.use_case.use_case_factory import ContextFactory
from src.app.properties.dev_properties import DevProperties
from src.app.reader.sib.dev_sib import DevSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib_interface import SibInterface
from src.app.widget import text_notification


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
        sib = ContextFactory().createSib(
            port,
            getReaderCalibrationFile(),
            readerNumber,
            portAllocator
        )
        success = sib.performHandshake()
        if success:
            text_notification.setText("Reader hardware connected successfully.")
            return sib
        else:
            logging.info(f"Failed to handshake SIB  on port {port}", extra={"id": "Sib"})
            text_notification.setText("Reader hardware disconnected.\nPlease contact your system administrator.")
            portAllocator.removePort(readerNumber)
            sib.close()
    except:
        logging.exception(f"Failed to connect to reader hardware.", extra={"id": "Sib"})
        portAllocator.removePort(readerNumber)


def getDesktopLocation():
    """ This gets the path to the computer's desktop. """
    try:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except KeyError:
        return os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')


def getReaderCalibrationFile() -> str:
    return f'{getDesktopLocation()}/Backend/Calibration/1/Calibration.csv'
