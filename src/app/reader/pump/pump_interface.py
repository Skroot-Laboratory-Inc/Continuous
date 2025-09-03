from reactivex.subject import BehaviorSubject

from src.app.model.sweep_data import SweepData


class PumpInterfaceMetaClass(type):
    """This checks that classes that implement SibInterface implement all members of the class"""
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'start') and
                callable(subclass.start) and
                hasattr(subclass, 'stop') and
                callable(subclass.stop) and
                hasattr(subclass, 'setSpeed') and
                callable(subclass.setSpeed) and
                hasattr(subclass, 'getToggleSubject') and
                callable(subclass.getToggleSubject))


class PumpInterface(metaclass=PumpInterfaceMetaClass):

    def start(self):
        """The reader takes a scan and returns magnitude values."""

    def stop(self):
        """The reader performs a calibration if needed."""

    def setSpeed(self, speed: float):
        """The reader loads in the calibration scan values."""

    def getToggleSubject(self) -> BehaviorSubject:
        """ Gets the behavior subject controlling the pump"""

