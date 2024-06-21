from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo


class PortAllocator:
    def __init__(self, os):
        self.ports = []
        self.os = os

    def getNewPort(self) -> (ListPortInfo, str):
        port = getNewPorts(self.os, self.ports)
        self.ports.append(port.device)
        return port

    def getMatchingPort(self, serialNumber) -> ListPortInfo:
        port = getMatchingPort(serialNumber)
        return port

    def removePort(self, port):
        self.ports.remove(port)

    def resetPorts(self):
        self.ports = []


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


def getMatchingPort(serialNumber) -> ListPortInfo:
    ports = list_ports.comports()
    port = [port.device for port in ports if port.serial_number == serialNumber][0]
    return port
