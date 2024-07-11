from src.app.model.sweep_data import SweepData


class AnalyzerInterfaceMetaClass(type):
    """This checks that classes that implement AnalyzerInterface implement all members of the class"""

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (
                hasattr(subclass, 'analyzeScan') and
                callable(subclass.analyzeScan) and
                hasattr(subclass, 'recordFailedScan') and
                callable(subclass.recordFailedScan) and
                hasattr(subclass, 'createAnalyzedFiles') and
                callable(subclass.createAnalyzedFiles) and
                hasattr(subclass, 'setZeroPoint') and
                callable(subclass.setZeroPoint) and
                hasattr(subclass, 'resetRun') and
                callable(subclass.resetRun))


class AnalyzerInterface(metaclass=AnalyzerInterfaceMetaClass):

    def analyzeScan(self, sweepData: SweepData, shouldDenoise):
        """ Analyzes the specified scan. """

    def recordFailedScan(self):
        """ Records a scan for when the SIB fails to take a scan. """

    def createAnalyzedFiles(self):
        """ Writes all analyzed files required. """

    def setZeroPoint(self, zeroPoint):
        """ Sets the zeroPoint to the specified value."""

    def resetRun(self):
        """ Resets the ResultSet to start at the current time. """

