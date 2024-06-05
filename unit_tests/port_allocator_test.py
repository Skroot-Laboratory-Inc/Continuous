import unittest

from mock import patch
from serial.tools.list_ports_common import ListPortInfo

import buttons
import port_allocator


class TestPortAllocatorMethods(unittest.TestCase):
    portParameters = [
        ("windows", "USB-SERIAL CH340", "VNA"),
        ("windows", "USB Serial Device", "SIB"),
        ("linux", "USB Serial", "VNA"),
        ("linux", "Skroot Laboratory", "SIB")
    ]

    @patch('serial.tools.list_ports.comports')
    def test_getNewVnaAndSibPorts(self, mockListComports):
        """
        Test that whether on Linux or Windows, the correct ports are found.
        """
        portTaken = ListPortInfo("COM6")
        for os, expectedDescription, expectedReaderType in self.portParameters:
            with self.subTest(os=os, expectedDescription=expectedDescription, expectedReaderType=expectedReaderType):
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
                portInfo, readerType = port_allocator.getNewVnaAndSibPorts(os, [portTaken])
                self.assertEqual(expectedReaderType, readerType)
                self.assertEqual("COM7", portInfo.device)

    def test_getNewVnaAndSibPortsReal(self):
        """
        Test used to connect to the reader and see information.
        """
        _, _ = port_allocator.getNewVnaAndSibPorts('windows', [])


if __name__ == '__main__':
    unittest.main()
