from src.resources.sibcontrol.sibcontrol import SIBException


class SIBReconnectException(SIBException):
    """Exception thrown when an error occurs but re-establishes correctly."""


class CancelSweepException(SIBException):
    """Exception thrown when a sweep is cancelled by the user."""


class NoSibFound(SIBException):
    """Exception thrown when a connection to the SIB is attempted but no SIB port is found."""

