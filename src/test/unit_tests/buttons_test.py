import unittest
from unittest import mock

from mock import patch

from src.app.initialization import buttons
from src.app.main_shared.main_shared import MainShared
from src.app.sib.sib import Sib


class TestButtonsMethods(unittest.TestCase):

    # This getDesktopLocation argument needs updated to work properly.
    @patch("src.app.helper.helper_functions.getDesktopLocation")
    @patch("src.app.sib.port_allocator.PortAllocator")
    @patch("src.app.sib.sib.Sib.__new__")
    def test_readerInstantiation(self, mockReaderInterface, mockPortAllocator, mockDesktopLocation):
        """
        Test that an Sib is instantiated with the correct arguments when instantiateReader is called
        """
        mockReaderInterface.return_value = mock.MagicMock()
        mockPortAllocator.return_value = mock.MagicMock()
        mockDesktopLocation.return_value = "/desktop"

        buttons.instantiateReader("COM7", mockPortAllocator, 1, False)

        mockReaderInterface.assert_called_with(Sib, "COM7", f'/desktop/Calibration/1/Calibration.csv', 1, mockPortAllocator, False)


if __name__ == '__main__':
    unittest.main()
