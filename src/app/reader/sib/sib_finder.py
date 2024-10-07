import logging
import time
from tkinter import messagebox

from src.app.exception.common_exceptions import UserExitedException
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.properties.dev_properties import DevProperties
from src.app.reader.sib.dev_sib import DevSib
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib import Sib
from src.app.reader.sib.sib_interface import SibInterface
from src.app.ui_manager.root_manager import RootManager
from src.app.widget import text_notification


class SibFinder:
    def __init__(self, rootManager: RootManager):
        self.PortAllocator = PortAllocator()
        self.RootManager = rootManager

    def connectSib(self, readerNumber, globalFileManager, calibrate: bool):
        if not DevProperties().isDevMode:
            try:
                port = self.findPort(readerNumber)
                return instantiateReader(port, self.PortAllocator, readerNumber, globalFileManager, calibrate)
            except UserExitedException:
                self.RootManager.destroyRoot()
                logging.exception("User exited during port finding.")
                raise
            except:
                logging.exception("Failed to connect new reader.")
        else:
            return DevSib(readerNumber)

    def findPort(self, readerNumber):
        filteredPorts, attempts, port = [], 0, ''
        pauseUntilUserClicks(readerNumber)
        while filteredPorts == [] and attempts <= 3:
            time.sleep(2)
            try:
                port = self.PortAllocator.getNewPort()
                return port
            except:
                attempts += 1
                if attempts > 3:
                    messagebox.showerror(
                        f'Reader {readerNumber}',
                        f'Reader {readerNumber}\nNew Reader not found more than 3 times,\nApp Restart required.')
                    break
                else:
                    shouldContinue = messagebox.askokcancel(
                        f'Reader {readerNumber}',
                        f'Reader {readerNumber}\nNew Reader not found, ensure a new Reader is plugged in, then press OK\n'
                        f'Press cancel to shutdown the app.')
                    if not shouldContinue:
                        break
        raise UserExitedException("The user chose not to go forward during port finding.")


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
            logging.info(f"Failed to handshake SIB #{readerNumber} on port {port}")
            text_notification.setText("Failed to connect to SiB")
            sib.close()
    except:
        portAllocator.removePort(port)
        logging.exception(f"Failed to instantiate reader {readerNumber}")


def pauseUntilUserClicks(readerNumber):
    messagebox.showinfo(f'Reader {readerNumber}',
                        f'Reader {readerNumber}\nPress OK when reader {readerNumber} is plugged in')