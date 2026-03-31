import logging
import threading
import time
import tkinter

import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from src.app.barcode_scanner.barcode import Barcode
from src.app.barcode_scanner.helpers.configuration import BarcodeConfiguration
from src.app.helper_methods.custom_exceptions.common_exceptions import NoBarcodeScannerFound
from src.app.properties.hardware_properties import HardwareProperties
from src.app.widget import text_notification


class BarcodeScanner:
    def __init__(self, scannedVesselId: tkinter.StringVar):
        self.scannedVesselId = scannedVesselId
        self.lastBarcodeScanned = None
        self.scanningActive = False
        try:
            self.barcodeScanner = serial.Serial(getBarcodePort().device, 9600, timeout=1)
            self.connected = True
        except NoBarcodeScannerFound:
            if BarcodeConfiguration().getConfig():
                text_notification.setText("Failed to connect to barcode scanner. Please reconnect.")
            logging.exception("Failed to connect barcode scanner.", extra={"id": "Barcode Scanner"})
            self.connected = False
        except Exception:
            logging.exception("Failed to connect barcode scanner.", extra={"id": "Barcode Scanner"})
            self.connected = False

    def start(self):
        self.scanningActive = True
        threading.Thread(target=self.scanBarcodes, daemon=True).start()

    def stop(self):
        self.scanningActive = False

    def scanBarcodes(self):
        while self.scanningActive:
            if self.connected:
                try:
                    if self.barcodeScanner.in_waiting > 0:
                        barcode = self.barcodeScanner.readline().decode('utf-8').strip()
                        self.lastBarcodeScanned = Barcode(barcode)
                        if self.lastBarcodeScanned.serial:
                            self.scannedVesselId.set(self.lastBarcodeScanned.serial)
                        else:
                            text_notification.setText(
                                "Invalid barcode. \nPlease ensure the barcode includes a serial number (GS1 field 21)."
                            )
                    time.sleep(0.1)
                except Exception:
                    self.resetBarcodeConnection()
            else:
                self.resetBarcodeConnection()
                time.sleep(2)

    def resetBarcodeConnection(self):
        try:
            self.barcodeScanner = serial.Serial(getBarcodePort().device, 9600, timeout=1)
            if BarcodeConfiguration().getConfig():
                text_notification.setText("Barcode scanner successfully reconnected.")
            self.connected = True
        except NoBarcodeScannerFound:
            if self.connected:
                logging.exception("Failed to connect barcode scanner.", extra={"id": "Barcode Scanner"})
                if BarcodeConfiguration().getConfig():
                    text_notification.setText("Failed to connect to barcode scanner. Please reconnect.")
            self.connected = False
        except Exception:
            logging.exception("Failed to connect barcode scanner.", extra={"id": "Barcode Scanner"})
            self.connected = False


def getBarcodePort() -> ListPortInfo:
    ports = list_ports.comports()
    orangeIds = [port for port in ports if HardwareProperties().ambirOrangeVendorId == port.vid]
    whiteIds = [port for port in ports if HardwareProperties().ambirWhiteVendorId == port.vid]
    filteredPorts = orangeIds + whiteIds
    if filteredPorts:
        return filteredPorts[0]
    raise NoBarcodeScannerFound()
