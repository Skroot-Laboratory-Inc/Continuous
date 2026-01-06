from abc import abstractmethod, ABC

from reactivex import Subject
from reactivex.subject import BehaviorSubject

from src.app.helper_methods.model.sweep_data import SweepData


class SibInterface(ABC):

    @abstractmethod
    def getCurrentlyScanning(self) -> Subject:
        """Returns whether the reader is currently scanning or not."""

    @abstractmethod
    def getCalibrationFilePresent(self) -> BehaviorSubject:
        """Returns whether the calibration file for the reader is present."""

    @abstractmethod
    def takeScan(self, directory: str, currentVolts: float, shutdown_flag=None) -> SweepData:
        """The reader takes a scan and returns magnitude values."""

    @abstractmethod
    def setReferenceFrequency(self, peakFrequencyMHz: float):
        """The reader sets the reference frequency according to the peak frequency."""

    @abstractmethod
    def estimateDuration(self) -> float:
        """Estimates the amount of time that a scan will take given its number of points. """

    @abstractmethod
    def performHandshake(self) -> bool:
        """The reader performs a handshake to establish communication."""

    @abstractmethod
    def performCalibration(self):
        """The reader performs a calibration."""

    @abstractmethod
    def loadCalibrationFile(self):
        """The reader loads in the calibration scan values."""

    @abstractmethod
    def takeCalibrationScan(self) -> bool:
        """The reader takes a scan using the calibration values for startFreq, stopFreq and nPoints."""

    @abstractmethod
    def setStartFrequency(self, startFreqMHz) -> bool:
        """The reader should implement a way to set the start frequency in MHz."""

    @abstractmethod
    def setStopFrequency(self, stopFreqMHz) -> bool:
        """The reader should implement a way to set the stop frequency in MHz."""

    @abstractmethod
    def close(self) -> bool:
        """The reader closes the port that it is using to connect."""

    @staticmethod
    def getYAxisLabel() -> str:
        """ Returns the yaxislabel, or units of the magnitude of the graph. """

