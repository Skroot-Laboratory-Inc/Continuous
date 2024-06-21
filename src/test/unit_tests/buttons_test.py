import unittest
from unittest import mock

from mock import patch

from src.app.initialization import buttons
from src.app.main_shared.main_shared import MainShared
from src.app.sib.sib import Sib


class TestButtonsMethods(unittest.TestCase):
    @patch("src.app.sib.port_allocator.PortAllocator")
    @patch("src.app.main_shared.main_shared.MainShared")
    @patch("src.app.sib.sib.Sib.__new__")
    def test_readerInstantiation(self, mockReaderInterface, mockAppModule, mockPortAllocator):
        """
        Test that an Sib is instantiated with the correct arguments when instantiateReader is called
        """
        mockReaderInterface.return_value = mock.MagicMock()
        mockPortAllocator.return_value = mock.MagicMock()
        mockAppModule.desktop = "/desktop"
        mockAppModule.PortAllocator = mockPortAllocator

        buttons.instantiateReader("COM7", mockAppModule, 1, False)

        mockReaderInterface.assert_called_with(Sib, "COM7", f'/desktop/Calibration/1/Calibration.csv', 1, mockPortAllocator, False)


if __name__ == '__main__':
    unittest.main()
