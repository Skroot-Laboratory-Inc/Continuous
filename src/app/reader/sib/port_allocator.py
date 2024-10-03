from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from src.app.helper.helper_functions import getOperatingSystem


class PortAllocator:
    def __init__(self):
        self.ports = []
        self.os = getOperatingSystem()

    def getNewPort(self) -> (ListPortInfo, str):
        port = getNewPorts(self.os, self.ports)
        self.ports.append(port.device)
        return port

    def removePort(self, port):
        self.ports.remove(port)

    @staticmethod
    def getMatchingPort(serialNumber) -> ListPortInfo:
        ports = list_ports.comports()
        port = [port.device for port in ports if port.serial_number == serialNumber][0]
        return port


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
