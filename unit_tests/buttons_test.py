import unittest
from unittest import mock

from mock import patch

import buttons
import sib


class TestButtonsMethods(unittest.TestCase):
    @patch("main_shared.MainShared")
    @patch("main_shared.MainShared")
    @patch("sib.Sib.__new__")
    def test_readerInstantiation(self, mockReaderInterface, mockAppModule, mockPortAllocator):
        """
        Test that an Sib is instantiated with the correct arguments when instantiateReader is called
        """
        mockReaderInterface.return_value = mock.MagicMock()
        mockPortAllocator.return_value = mock.MagicMock()
        mockAppModule.desktop = "/desktop"
        mockAppModule.PortAllocator = mockPortAllocator

        buttons.instantiateReader("COM7", mockAppModule, 1, False)

        mockReaderInterface.assert_called_with(sib.Sib, "COM7", f'/desktop/Calibration/1/Calibration.csv', 1, mockPortAllocator, False)


if __name__ == '__main__':
    unittest.main()
