class AnalysisException(Exception):
    """Base exception class for the analysis related exceptions."""


class BadFitException(AnalysisException):
    """Exception thrown when the fitting function fails to fit the data."""


class ZeroPointException(Exception):
    """Exception thrown when an error occurs calculating the zeroPoint."""


class RawScanException(AnalysisException):
    """Exception thrown when an error occurs analyzing the raw scan."""


class SmoothedScanException(AnalysisException):
    """Exception thrown when an error occurs analyzing the smoothed scan."""



