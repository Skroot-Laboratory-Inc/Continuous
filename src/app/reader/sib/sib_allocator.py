import logging
import time
from tkinter import messagebox

from src.app.exception.common_exceptions import UserExitedException
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.properties.dev_properties import DevProperties
from src.app.reader.sib.port_allocator import PortAllocator
from src.app.reader.sib.sib import Sib
from src.app.reader.sib.sib_interface import SibInterface
from src.app.widget import text_notification


class SibAllocator:
    def __init__(self, globalFileManager: GlobalFileManager):
        self.isDevMode = DevProperties().isDevMode
        self.PortAllocator = PortAllocator()
        self.GlobalFileManager = globalFileManager
        self.SibInterfaces = {}

    def getNewSib(self, readerNumber):
        try:
            port = self.findPort(readerNumber)
            self.SibInterfaces[readerNumber] = self.instantiateReader(port, readerNumber, False)
        except UserExitedException:
            logging.exception("User exited during port finding.")
            raise

    def getSib(self, readerNumber):
        return self.SibInterfaces[readerNumber]

    def removeSib(self, readerNumber, port):
        self.PortAllocator.removePort(port)
        del self.SibInterfaces[readerNumber]

    def resetPorts(self):
        self.SibInterfaces = {}

    def findPort(self, readerNumber):
        if not self.isDevMode:
            filteredPorts, attempts, port = [], 0, ''
            self.pauseUntilUserClicks(readerNumber)
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
        else:
            return '', ''

    def instantiateReader(self, port, readerNumber, calibrationRequired) -> SibInterface:
        try:
            sib = Sib(
                port,
                ReaderFileManager(self.GlobalFileManager, readerNumber).getCalibrationGlobalLocation(),
                readerNumber,
                self.PortAllocator,
                calibrationRequired,
            )
            if sib.performHandshake():
                return sib
            else:
                logging.info(f"Failed to handshake SIB #{readerNumber} on port {port}")
                text_notification.setText("Failed to connect to SiB")
                sib.close()
        except:
            logging.exception(f"Failed to instantiate reader {readerNumber}")

    @staticmethod
    def pauseUntilUserClicks(readerNumber):
        messagebox.showinfo(
            f'Reader {readerNumber}',
            f'Reader {readerNumber}\nPress OK when reader {readerNumber} is plugged in'
        )

