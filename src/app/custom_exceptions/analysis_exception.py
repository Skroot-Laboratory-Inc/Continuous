class AnalysisException(Exception):
    """ Base custom_exceptions class for the analysis related exceptions. """


class ZeroPointException(Exception):
    """Exception thrown when an error occurs calculating the zeroPoint."""


class SensorNotFoundException(Exception):
    """ Exception thrown when the sensor data is not found above the antenna. """
    def __init__(self, message):
        self.message = message


class FocusedSweepFailedException(Exception):
    """ Exception thrown when the sensor data is not found above the antenna. """


class BadFitException(AnalysisException):
    """ Exception thrown when the fitting function fails to fit the data. """


class ScanAnalysisException(AnalysisException):
    """ Exception thrown when an error occurs analyzing the raw scan. """

