import logging
import time
from tkinter import messagebox

from src.app.exception.common_exceptions import UserExitedException
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.helper.helper_functions import getOperatingSystem
from src.app.properties.dev_properties import DevProperties
from src.app.reader.sib.dev_sib import DevSib
from src.app.reader.sib.hub_port_allocator import HubPortAllocator
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib import Sib
from src.app.reader.sib.sib_interface import SibInterface
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification


class SibFinder:
    def __init__(self, rootManager: RootManager):
        if getOperatingSystem() == "windows":
            self.PortAllocator = PortAllocator()
        else:
            self.PortAllocator = HubPortAllocator()
        self.RootManager = rootManager

    def connectSib(self, readerNumber, globalFileManager, calibrate: bool):
        if not DevProperties().isDevMode:
            try:
                port = self.findPort(readerNumber)
                return instantiateReader(port, self.PortAllocator, readerNumber, globalFileManager, calibrate)
            except UserExitedException:
                self.RootManager.destroyRoot()
                logging.exception("User exited during port finding.", extra={"id": f"Reader {readerNumber}"})
                raise
            except:
                logging.exception("Failed to connect new reader.", extra={"id": f"Reader {readerNumber}"})
        else:
            return DevSib(readerNumber)

    def findPort(self, readerNumber):
        filteredPorts, attempts, port = [], 0, ''
        pauseUntilUserClicks(readerNumber)
        while filteredPorts == [] and attempts <= 3:
            time.sleep(2)
            try:
                port = self.PortAllocator.getPortForReader(readerNumber)
                return port
            except:
                attempts += 1
                if attempts > 3:
                    messagebox.showinfo(
                        f'Reader {readerNumber}',
                        f'Failed to connect to Reader {readerNumber}. Cancelling connection.')
                else:
                    shouldContinue = messagebox.askokcancel(
                        f'Reader {readerNumber}',
                        f'Reader {readerNumber} not found\n'
                        f'Please plug in Vessel {readerNumber} then press OK\n'
                        'Press cancel to cancel the connection process.')
                    if not shouldContinue:
                        break


def instantiateReader(port, portAllocator, readerNumber, globalFileManager, calibrationRequired) -> SibInterface:
    try:
        sib = Sib(
            port,
            ReaderFileManager(globalFileManager, readerNumber).getCalibrationGlobalLocation(),
            readerNumber,
            portAllocator,
            calibrationRequired,
        )
        success = sib.performHandshake()
        if success:
            return sib
        else:
            logging.info(f"Failed to handshake SIB #{readerNumber} on port {port}", extra={"id": f"Reader {readerNumber}"})
            text_notification.setText("Failed to connect to SiB")
            sib.close()
    except:
        portAllocator.removePort(port)
        logging.exception(f"Failed to instantiate reader.", extra={"id": f"Reader {readerNumber}"})


def pauseUntilUserClicks(readerNumber):
    messagebox.showinfo(f'Reader {readerNumber}',
                        f'Reader {readerNumber}\nPress OK when reader {readerNumber} is plugged in')
