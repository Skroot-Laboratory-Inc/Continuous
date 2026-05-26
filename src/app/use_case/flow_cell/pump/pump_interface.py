from abc import ABC, abstractmethod

from reactivex.subject import BehaviorSubject


class PumpInterface(ABC):

    @abstractmethod
    def start(self):
        """ Starts the pump."""

    @abstractmethod
    def stop(self):
        """ Stops the pump"""

    @abstractmethod
    def setRpm(self, rpm: float):
        """Sets the motor RPM driving the pump."""

    @abstractmethod
    def getToggleSubject(self) -> BehaviorSubject:
        """ Gets the behavior subject controlling the pump"""
