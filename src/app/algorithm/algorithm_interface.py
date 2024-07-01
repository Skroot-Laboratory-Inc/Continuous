from typing import List

from src.app.model.result_set import ResultSet
from src.app.model.sweep_data import SweepData


class AlgorithmInterfaceMetaClass(type):
    """This checks that classes that implement AlgorithmInterface implement all members of the class"""
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'check') and
                callable(subclass.check) and
                hasattr(subclass, 'getStatus') and
                callable(subclass.getStatus))


class AlgorithmInterface(metaclass=AlgorithmInterfaceMetaClass):

    def check(self, resultSet: ResultSet):
        """The prompts the algorithm to recalculate its status."""

    def getStatus(self) -> bool:
        """Returns a bool reresentating the state of the algorithm."""
