import tkinter as tk


class PopupInterfaceMetaClass(type):
    """This checks that classes that implement SibInterface implement all members of the class"""

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'fillOutWindowFn') and
                callable(subclass.fillOutWindowFn))


class PopupInterface(metaclass=PopupInterfaceMetaClass):

    def fillOutWindowFn(self, window: tk.Frame):
        """ This populates the popup with whatever widgets are required. """
