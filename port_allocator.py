from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo


class PortAllocator:
    def __init__(self, os):
        self.ports = []
        self.os = os

    def getNewPort(self) -> (ListPortInfo, str):
        port, readerType = getNewVnaAndSibPorts(self.os, self.ports)
        self.ports.append(port)
        return port, readerType

    def removePort(self, port):
        self.ports.remove(port)

    def resetPorts(self):
        self.ports = []


def getNewVnaAndSibPorts(currentOs, portsTaken) -> (ListPortInfo, str):
    ports = list_ports.comports()
    if currentOs == "windows":
        filteredVNAPorts = [port.device for port in ports if
                            "USB-SERIAL CH340" in port.description and port.device not in portsTaken]
        filteredSIBPorts = [port.device for port in ports if
                            "USB Serial Device" in port.description and port.device not in portsTaken]
    else:
        filteredVNAPorts = [port.device for port in ports
                            if port.description == "USB Serial" and port.device not in portsTaken]
        filteredSIBPorts = [port.device for port in ports if
                            port.manufacturer == "Skroot Laboratory" and port.device not in portsTaken]
    if filteredSIBPorts:
        return filteredSIBPorts[0], 'SIB'
    if filteredVNAPorts:
        return filteredVNAPorts[0], 'VNA'
    raise Exception("No ports found")