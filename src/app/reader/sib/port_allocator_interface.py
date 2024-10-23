from serial.tools.list_ports_common import ListPortInfo


class PortAllocatorInterfaceMetaClass(type):
    """This checks that classes that implement SibInterface implement all members of the class"""
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'getNewPort') and
                callable(subclass.getPortForReader) and
                hasattr(subclass, 'removePort') and
                callable(subclass.removePort) and
                hasattr(subclass, 'getPowerStatus') and
                callable(subclass.getPowerStatus) and
                hasattr(subclass, 'resetPorts') and
                callable(subclass.resetPorts))


class PortAllocatorInterface(metaclass=PortAllocatorInterfaceMetaClass):

    def getPortForReader(self, readerNumber: str) -> ListPortInfo:
        """ Allocates a new port and returns the entire port. """

    def removePort(self, readerNumber: str):
        """ Removes a port from the list of ports currently in use. """

    def getPowerStatus(self, readerNumber: str) -> str:
        """ Gets the port's power status for a given readerNumber. """

    def resetPorts(self):
        """ Resets ports allocated to readers. """

