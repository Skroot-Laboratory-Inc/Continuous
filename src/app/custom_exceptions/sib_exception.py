from src.resources.sibcontrol.sibcontrol import SIBException


class SIBReconnectException(SIBException):
    """Exception thrown when an error occurs but re-establishes correctly."""


class NoSibFound(SIBException):
    """Exception thrown when a connection to the SIB is attempted but no SIB port is found."""

