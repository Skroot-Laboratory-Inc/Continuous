
class SIBException(Exception):
    '''Base exception class for the sib controller exceptions.'''

class SIBConnectionError(SIBException):
    '''Exception used when port cannot be opened or when read/write
    operations are attempted when port is not open.'''

class SIBTimeoutError(SIBException):
    '''Exception used for timeouts during read/write operations.'''

class SIBError(SIBException):
    '''Raised when the host detects unexpected behavior from the SIB.'''

class SIBACKException(SIBException):
    '''Exception used to detect when the system sends the FAIL acknowledgmeent.'''

class SIBInvalidCommandError(SIBACKException):
    '''The host has received the Invalid Command error from the SIB.'''

class SIBDDSConfigError(SIBACKException):
    '''The host has received the DDS configuration error from the SIB.'''

class SIBRegulatorsNotReadyError(SIBACKException):
    '''The host has received the Regulators not Ready error from the SIB.'''

