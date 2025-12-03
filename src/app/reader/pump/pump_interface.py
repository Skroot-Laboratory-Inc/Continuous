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
    def setFlowRate(self, flowRate: float):
        """ Sets the flowrate for the pump class."""

    @abstractmethod
    def getToggleSubject(self) -> BehaviorSubject:
        """ Gets the behavior subject controlling the pump"""
