import unittest
from unittest import mock
from unittest.mock import patch

from serial.tools.list_ports_common import ListPortInfo

from src.app.reader.sib.hub_port_allocator import HubPortAllocator
from src.app.uhubctl.usb import Hub


def createHub(hubId: str, portNumber: int, mockPort: mock.MagicMock) -> Hub:
    hub = Hub(hubId)
    mockPort.port_number.return_value = portNumber
    mockPort.toString.return_value = f"{hub.path}.{portNumber}"
    mockPort.vendor_id.return_value = 8263
    mockPort.description.return_value = "Skroot Laboratory SIB350 SERIAL0"
    hub.ports = [mockPort]
    return hub


def createComPortObject(comport: str) -> ListPortInfo:
    expectedPortObject = ListPortInfo(comport)
    expectedPortObject.serial_number = "SERIAL0"
    expectedPortObject.manufacturer = "Skroot Laboratory"
    expectedPortObject.product = "SIB350"
    return expectedPortObject


class TestHubPortAllocatorMethods(unittest.TestCase):

    @patch('src.app.uhubctl.usb.Port')
    @patch('src.app.uhubctl.usb.discover_hubs')
    @patch('serial.tools.list_ports.comports')
    def test_scanForPorts(self, mockListComports, mockDiscoverHubs, mockPort):
        """
        Test that ports are found correctly and assigned the correct reader
        """
        mockPort.return_value = mock.MagicMock()
        mockDiscoverHubs.return_value = [createHub("1-1", 4, mockPort)]
        mockListComports.return_value = [createComPortObject("COM7")]

        portAllocator = HubPortAllocator()
        self.assertEqual(
            portAllocator.readerPhysicalPortMap[1].device,
            "COM7"
        )


if __name__ == '__main__':
    unittest.main()
