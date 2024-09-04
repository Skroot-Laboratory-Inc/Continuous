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
                hasattr(subclass, 'uploadExperimentCsv') and
                callable(subclass.uploadExperimentFilesOnInterval) and
                hasattr(subclass, 'uploadExperimentLog') and
                callable(subclass.uploadExperimentLog))


class AwsServiceInterface(metaclass=AwsServiceInterfaceMetaClass):

    def checkForSoftwareUpdate(self):
        """ Checks if a software update is required. """

    def downloadSoftwareUpdate(self):
        """ Downloads the software update identified in `checkForSoftwareUpdate`. """

    def uploadExperimentFilesOnInterval(self, scanNumber, guidedSetupForm):
        """ Uploads the summary csv for the experiment. """

    def uploadFinalExperimentFiles(self, guidedSetupForm):
        """ Uploads the summary csv for the experiment. """

    def uploadExperimentLog(self):
        """ Uploads the log file for the experiment. """

    def uploadIssueLog(self):
        """ Uploads the issue log to AWS in the experiment folder. """

    def downloadIssueLog(self):
        """ Downloads the issue log for the experiment, if present. """

