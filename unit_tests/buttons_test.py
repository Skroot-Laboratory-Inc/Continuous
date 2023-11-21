import unittest
from unittest import mock

from mock import patch
from serial.tools.list_ports_common import ListPortInfo

import buttons
import sib
import vna


class TestButtonsMethods(unittest.TestCase):
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
                if os == "linux" and expectedDescription == "Skroot Laboratory":
                    expectedPortObject.manufacturer = expectedDescription
                else:
                    expectedPortObject.description = expectedDescription
                mockListComports.return_value = [expectedPortObject]
                portInfo, readerType = buttons.getNewVnaAndSibPorts(os, [portTaken])
                self.assertEqual(expectedReaderType, readerType)
                self.assertEqual("COM7", portInfo)

    @patch("main_shared.MainShared")
    @patch("vna.VnaScanning.__new__")
    def test_readerInstantiationVna(self, mockReaderInterface, mockAppModule):
        """
        Test that a Vna is instantiated when instantiateReader is called with readerType 'VNA'
        """
        mockReaderInterface.return_value = mock.MagicMock()

        buttons.instantiateReader('VNA', "COM7", mockAppModule, 1, False)

        mockReaderInterface.assert_called_with(vna.VnaScanning, "COM7", mockAppModule, 1, False)

    @patch("main_shared.MainShared")
    @patch("sib.Sib.__new__")
    def test_readerInstantiationSib(self, mockReaderInterface, mockAppModule):
        """
        Test that an Sib is instantiated when instantiateReader is called with readerType 'SIB'
        """
        mockReaderInterface.return_value = mock.MagicMock()

        buttons.instantiateReader('SIB', "COM7", mockAppModule, 1, False)

        mockReaderInterface.assert_called_with(sib.Sib, "COM7", mockAppModule, 1, False)


if __name__ == '__main__':
    unittest.main()
