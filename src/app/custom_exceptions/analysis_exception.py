class AnalysisException(Exception):
    """ Base custom_exceptions class for the analysis related exceptions. """


class BadFitException(AnalysisException):
    """ Exception thrown when the fitting function fails to fit the data. """


class ZeroPointException(Exception):
    """Exception thrown when an error occurs calculating the zeroPoint."""


class ScanAnalysisException(AnalysisException):
    """ Exception thrown when an error occurs analyzing the raw scan. """

