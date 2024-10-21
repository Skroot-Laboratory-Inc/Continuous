from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from src.app.helper.helper_functions import getOperatingSystem
from src.app.reader.sib.port_allocator_interface import PortAllocatorInterface


class PortAllocator(PortAllocatorInterface):
    def __init__(self):
        self.ports = {}
        self.os = getOperatingSystem()

    def getPortForReader(self, readerNumber) -> ListPortInfo:
        if readerNumber in self.ports:
            return self.ports[readerNumber]
        port = getNewPorts(self.os, self.ports.values())
        self.ports[readerNumber] = port.device
        return port

    def removePort(self, readerNumber):
        del self.ports[readerNumber]

    def resetPorts(self):
        self.ports = {}


def getNewPorts(currentOs, portsTaken) -> ListPortInfo:
    ports = list_ports.comports()
    if currentOs == "windows":
        filteredPorts = [port for port in ports if
                            "USB Serial Device" in port.description and port.device not in portsTaken]
    else:
        filteredPorts = [port for port in ports if
                            port.manufacturer == "Skroot Laboratory" and port.device not in portsTaken]
    if filteredPorts:
        return filteredPorts[0]
    raise Exception("No ports found")
