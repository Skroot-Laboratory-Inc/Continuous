from typing import List

from src.app.model.sweep_data import SweepData
from src.app.reader.reader import Reader


class AwsServiceInterfaceMetaClass(type):
    """This checks that classes that implement AwsServiceInterface implement all members of the class"""

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (
                hasattr(subclass, 'checkForSoftwareUpdate') and
                callable(subclass.checkForSoftwareUpdate) and
                hasattr(subclass, 'downloadSoftwareUpdate') and
                callable(subclass.downloadSoftwareUpdate) and
                hasattr(subclass, 'uploadSummaryPdf') and
                callable(subclass.uploadSummaryPdf) and
                hasattr(subclass, 'uploadExperimentLog') and
                callable(subclass.uploadExperimentLog))


class AwsServiceInterface(metaclass=AwsServiceInterfaceMetaClass):

    def checkForSoftwareUpdate(self):
        """ Checks if a software update is required. """

    def downloadSoftwareUpdate(self):
        """ Downloads the software update identified in `checkForSoftwareUpdate`. """

    def uploadSummaryPdf(self, scanNumber):
        """ Uploads the summary pdf for the experiment. """

    def uploadExperimentLog(self):
        """ Uploads the log file for the experiment. """

