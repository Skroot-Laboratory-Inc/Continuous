from src.app.model.plottable import Plottable
from src.app.model.result_set import ResultSet
from src.app.model.sweep_data import SweepData
from src.app.reader.analyzer.analyzer import Analyzer


class ReaderInterfaceMetaClass(type):
    """This checks that classes that implement ReaderInterface implement all members of the class"""

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (
                hasattr(subclass, 'addToPdf') and
                callable(subclass.addToPdf) and
                hasattr(subclass, 'addInoculationMenuBar') and
                callable(subclass.addInoculationMenuBar) and
                hasattr(subclass, 'addSecondAxisMenubar') and
                callable(subclass.addSecondAxisMenubar) and
                hasattr(subclass, 'addExperimentNotesMenubar') and
                callable(subclass.addExperimentNotesMenubar) and
                hasattr(subclass, 'getCurrentPlottable') and
                callable(subclass.getCurrentPlottable) and
                hasattr(subclass, 'getAnalyzer') and
                callable(subclass.getAnalyzer) and
                hasattr(subclass, 'getResultSet') and
                callable(subclass.getResultSet) and
                hasattr(subclass, 'getZeroPoint') and
                callable(subclass.getZeroPoint) and
                hasattr(subclass, 'resetReaderRun') and
                callable(subclass.resetReaderRun))


class ReaderInterface(metaclass=ReaderInterfaceMetaClass):

    def addToPdf(self, pdf, x, y, indicatorRadius, totalWidth, totalHeight):
        """The reader takes a scan and returns magnitude values."""

    def addInoculationMenuBar(self, menu):
        """ Creates the menubar option to inoculate the Reader."""

    def addSecondAxisMenubar(self, menu):
        """ Creates the menubar option to add second axis values to the Reader."""

    def addExperimentNotesMenubar(self, menu):
        """ Creates the menubar option to add experiment notes to the Reader."""

    def getCurrentPlottable(self, denoiseSet) -> Plottable:
        """ Gets the current plottable data for the Reader. """

    def getAnalyzer(self) -> Analyzer:
        """ Gets the analyzer for the Reader."""

    def getResultSet(self) -> ResultSet:
        """ Gets the current ResultSet for the reader."""

    def getZeroPoint(self):
        """ Gets the calculated zero point for the Reader."""

    def resetReaderRun(self):
        """ Resets all Reader data for the end of a run."""
