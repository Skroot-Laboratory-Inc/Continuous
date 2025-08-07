import platform

from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo


class PortAllocator:
    def __init__(self):
        self.ports = {}

    def getPortForReader(self, readerNumber) -> ListPortInfo:
        if readerNumber in self.ports:
            return self.ports[readerNumber]
        port = getNewPorts(self.ports.values())
        self.ports[readerNumber] = port.device
        return port

    def removePort(self, readerNumber):
        del self.ports[readerNumber]

    def resetPorts(self):
        self.ports = {}


def getNewPorts(portsTaken) -> ListPortInfo:
    ports = list_ports.comports()
    if platform.system() == "Windows":
        filteredPorts = [port for port in ports if
                            "USB Serial Device" in port.description and port.device not in portsTaken]
    else:
        filteredPorts = [port for port in ports if
                            port.manufacturer == "Skroot Laboratory" and port.device not in portsTaken]
    if filteredPorts:
        return filteredPorts[0]
    raise Exception("No ports found")
