from reactivex import Subject
from reactivex.subject import BehaviorSubject

from src.app.model.sweep_data import SweepData


class SibInterfaceMetaClass(type):
    """This checks that classes that implement SibInterface implement all members of the class"""
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'takeScan') and
                callable(subclass.takeScan) and
                hasattr(subclass, 'estimateDuration') and
                callable(subclass.estimateDuration) and
                hasattr(subclass, 'takeCalibrationScan') and
                callable(subclass.takeCalibrationScan) and
                hasattr(subclass, 'performCalibration') and
                callable(subclass.performCalibration) and
                hasattr(subclass, 'loadCalibrationFile') and
                callable(subclass.loadCalibrationFile) and
                hasattr(subclass, 'setStartFrequency') and
                callable(subclass.setStartFrequency) and
                hasattr(subclass, 'setStopFrequency') and
                callable(subclass.setStopFrequency) and
                hasattr(subclass, 'getYAxisLabel') and
                callable(subclass.getYAxisLabel) and
                hasattr(subclass, 'getCurrentlyScanning') and
                callable(subclass.getCurrentlyScanning) and
                hasattr(subclass, 'getCalibrationFilePresent') and
                callable(subclass.getCalibrationFilePresent) and
                hasattr(subclass, 'close') and
                callable(subclass.close))


class SibInterface(metaclass=SibInterfaceMetaClass):

    def getCurrentlyScanning(self) -> Subject:
        """Returns whether the reader is currently scanning or not."""

    def getCalibrationFilePresent(self) -> BehaviorSubject:
        """Returns whether the calibration file for the reader is present."""

    def takeScan(self, outputFilename, disableSaveFiles) -> SweepData:
        """The reader takes a scan and returns magnitude values."""

    def estimateDuration(self) -> float:
        """Estimates the amount of time that a scan will take given its number of points. """

    def performCalibration(self):
        """The reader performs a calibration."""

    def loadCalibrationFile(self):
        """The reader loads in the calibration scan values."""

    def takeCalibrationScan(self) -> bool:
        """The reader takes a scan using the calibration values for startFreq, stopFreq and nPoints."""

    def setStartFrequency(self, startFreqMHz) -> bool:
        """The reader should implement a way to set the start frequency in MHz."""

    def setStopFrequency(self, stopFreqMHz) -> bool:
        """The reader should implement a way to set the stop frequency in MHz."""

    def close(self) -> bool:
        """The reader closes the port that it is using to connect."""

    def getYAxisLabel(self) -> str:
        """ Returns the yaxislabel, or units of the magnitude of the graph. """

