from typing import List


class ReaderInterfaceMetaClass(type):
    """This checks that classes that implement ReaderInterface implement all members of the class"""
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'takeScan') and
                callable(subclass.takeScan) and
                hasattr(subclass, 'takeCalibrationScan') and
                callable(subclass.takeCalibrationScan) and
                hasattr(subclass, 'calibrateIfRequired') and
                callable(subclass.calibrateIfRequired) and
                hasattr(subclass, 'loadCalibrationFile') and
                callable(subclass.loadCalibrationFile) and
                hasattr(subclass, 'setStartFrequency') and
                callable(subclass.setStartFrequency) and
                hasattr(subclass, 'setStopFrequency') and
                callable(subclass.setStopFrequency) and
                hasattr(subclass, 'close') and
                callable(subclass.close))


class ReaderInterface(metaclass=ReaderInterfaceMetaClass):

    def takeScan(self, outputFilename) -> (List[float], List[float], List[float], bool):
        """The reader takes a scan and returns magnitude values."""

    def calibrateIfRequired(self):
        """The reader performs a calibration if needed."""

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

