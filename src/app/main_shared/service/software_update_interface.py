class SoftwareUpdateInterfaceMetaClass(type):
    """This checks that classes that implement AwsServiceInterface implement all members of the class"""

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (
                hasattr(subclass, 'downloadSoftwareUpdate') and
                callable(subclass.downloadSoftwareUpdate) and
                hasattr(subclass, 'checkForSoftwareUpdates') and
                callable(subclass.checkForSoftwareUpdates))


class SoftwareUpdateInterface(metaclass=SoftwareUpdateInterfaceMetaClass):

    def downloadSoftwareUpdate(self):
        """ Downloads the software update and extracts it to it's folder. """

    def checkForSoftwareUpdates(self):
        """ Checks if a newer version of the software is available for download. """

