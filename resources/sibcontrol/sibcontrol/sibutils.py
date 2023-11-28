
class SIBException(Exception):
    '''Base exception class for the sib controller exceptions.'''

class SIBConnectionError(SIBException):
    '''Exception used when port cannot be opened or when read/write
    operations are attempted when port is not open.'''

class SIBTimeoutError(SIBException):
    '''Exception used for timeouts during read/write operations.'''

class SIBACKException(SIBException):
    '''Exception used to detect when the system sends the FAIL acknowledgmeent.'''