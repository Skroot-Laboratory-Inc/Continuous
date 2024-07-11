import unittest

from mock import patch
from serial.tools.list_ports_common import ListPortInfo

from src.app.reader.sib import port_allocator


class TestPortAllocatorMethods(unittest.TestCase):
    portParameters = [
        ("windows", "USB Serial Device"),
        ("linux", "Skroot Laboratory")
    ]

    @patch('serial.tools.list_ports.comports')
    def test_getNewPorts(self, mockListComports):
        """
        Test that whether on Linux or Windows, the correct ports are found.
        """
        portTaken = ListPortInfo("COM6")
        for os, expectedDescription in self.portParameters:
            with self.subTest(os=os, expectedDescription=expectedDescription):
                if os == "linux" and expectedDescription == "Skroot Laboratory":
                    portTaken.manufacturer = expectedDescription
                else:
                    portTaken.description = expectedDescription
                expectedPortObject = ListPortInfo("COM7")
                expectedPortObject.serial_number = "serial_number"
                if os == "linux" and expectedDescription == "Skroot Laboratory":
                    expectedPortObject.manufacturer = expectedDescription
                else:
                    expectedPortObject.description = expectedDescription
                mockListComports.return_value = [expectedPortObject]
                portInfo = port_allocator.getNewPorts(os, [portTaken])
                self.assertEqual("COM7", portInfo.device)

    def test_getNewPortsReal(self):
        """
        Test used to connect to the reader and see information.
        """
        _, _ = port_allocator.getNewPorts('windows', [])


if __name__ == '__main__':
    unittest.main()
