from sibcontrol import SIBException


class SIBReconnectException(SIBException):
    """Exception thrown when an error occurs but re-establishes correctly."""