class ButtonInterfaceMetaClass(type):
    """This checks that classes that implement ReaderInterface implement all members of the class"""

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (
                hasattr(subclass, 'place') and
                callable(subclass.place) and
                hasattr(subclass, 'destroySelf') and
                callable(subclass.destroySelf))


class ButtonInterface(metaclass=ButtonInterfaceMetaClass):

    def place(self):
        """ Places the button on `master`."""

    def destroySelf(self):
        """ Destroys the button on the Tkinter interface. """

