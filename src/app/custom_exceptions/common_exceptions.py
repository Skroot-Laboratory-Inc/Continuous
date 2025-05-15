class USBDriveNotFoundException(Exception):
    """ Exception raised when searching for a USB and not finding one. """


class UserConfirmationException(Exception):
    """ Exception raised when the user does not confirm an action. """


class NoBarcodeScannerFound(Exception):
    """ Exception thrown when a connection is attempted with the barcode but no ports are found. """
