import threading

from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from src.app.helper.helper_functions import getSibPowerStatus
from src.app.properties.hardware_properties import HardwareProperties
from src.app.reader.sib.port_allocator_interface import PortAllocatorInterface
from src.app.uhubctl import usb
from src.app.widget import text_notification


class HubPortAllocator(PortAllocatorInterface):
    def __init__(self):
        self.skrootVendorId = HardwareProperties().skrootVendorId
        self.skrootManufacturer = HardwareProperties().skrootManufacturer
        self.virtualPortDescriptionMap = {}
        self.descriptionComPortMap = {}
        self.readerPhysicalPortMap = {}
        self.readerVirtualPortMap = {}
        self.thread = threading.Thread(target=self.scanForPorts, args=(), daemon=True)
        self.thread.start()

    def getPortForReader(self, readerNumber) -> ListPortInfo:
        if self.thread.is_alive():
            self.thread.join()
        if readerNumber in self.readerPhysicalPortMap:
            return self.readerPhysicalPortMap[readerNumber]
        else:
            self.scanForPorts()
            if readerNumber in self.readerPhysicalPortMap:
                return self.readerPhysicalPortMap[readerNumber]
            else:
                text_notification.setText(
                    f"Please ensure that Vessel {readerNumber} is plugged in, then try connecting again."
                )
            raise Exception()

    def scanForPorts(self):
        self.resetPorts()
        for hub in usb.discover_hubs():
            for port in filter(lambda p: p.vendor_id() == self.skrootVendorId, hub.ports):
                self.virtualPortDescriptionMap[port.toString()] = port.description()
                self.readerVirtualPortMap = self.createVirtualPortMap(hub.get_short_path())

        for port in filter(lambda p: p.manufacturer == self.skrootManufacturer, list_ports.comports()):
            self.descriptionComPortMap[f"{port.manufacturer} {port.product} {port.serial_number}"] = port

        for description, physicalPort in self.descriptionComPortMap.items():
            virtualPort = getDictKeyByValue(self.virtualPortDescriptionMap, description)
            readerNumber = getDictKeyByValue(self.readerVirtualPortMap, virtualPort)
            self.readerPhysicalPortMap[readerNumber] = physicalPort

    def removePort(self, readerNumber: str):
        # Here for backwards compatibility with windows.
        pass
    
    def getPortPowerStatus(self, readerNumber: str):
        return getSibPowerStatus(self.readerVirtualPortMap[readerNumber])

    def resetPorts(self):
        self.virtualPortDescriptionMap = {}
        self.descriptionComPortMap = {}
        self.readerPhysicalPortMap = {}
        self.readerVirtualPortMap = {}

    @staticmethod
    def createVirtualPortMap(hubShortPath):
        return {
            1: f"{hubShortPath}.4",
            2: f"{hubShortPath}.3",
            3: f"{hubShortPath}.2",
            4: f"{hubShortPath}.1.4",
            5: f"{hubShortPath}.1.3",
            6: f"{hubShortPath}.1.2",
            7: f"{hubShortPath}.1.1.4",
            8: f"{hubShortPath}.1.1.3",
            9: f"{hubShortPath}.1.1.2",
            10: f"{hubShortPath}.1.1.1",
        }


def getDictKeyByValue(dictionary, searchValue):
    for key, value in dictionary.items():
        if value == searchValue:
            return key
    return None
