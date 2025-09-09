from reactivex.subject import BehaviorSubject


class PumpInterfaceMetaClass(type):
    """This checks that classes that implement SibInterface implement all members of the class"""
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'start') and
                callable(subclass.start) and
                hasattr(subclass, 'stop') and
                callable(subclass.stop) and
                hasattr(subclass, 'setFlowRate') and
                callable(subclass.setFlowRate) and
                hasattr(subclass, 'getToggleSubject') and
                callable(subclass.getToggleSubject))


class PumpInterface(metaclass=PumpInterfaceMetaClass):

    def start(self):
        """ Starts the pump."""

    def stop(self):
        """ Stops the pump"""

    def setFlowRate(self, flowRate: float):
        """ Sets the flowrate for the pump class."""

    def getToggleSubject(self) -> BehaviorSubject:
        """ Gets the behavior subject controlling the pump"""

