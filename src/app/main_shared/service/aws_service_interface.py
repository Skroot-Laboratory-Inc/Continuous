class AwsServiceInterfaceMetaClass(type):
    """This checks that classes that implement AwsServiceInterface implement all members of the class"""

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (
                hasattr(subclass, 'uploadExperimentFilesOnInterval') and
                callable(subclass.uploadExperimentFilesOnInterval) and
                hasattr(subclass, 'uploadFinalExperimentFiles') and
                callable(subclass.uploadFinalExperimentFiles) and
                hasattr(subclass, 'uploadExperimentLog') and
                callable(subclass.uploadExperimentLog) and
                hasattr(subclass, 'uploadIssueLog') and
                callable(subclass.uploadIssueLog) and
                hasattr(subclass, 'downloadIssueLogIfModified') and
                callable(subclass.downloadIssueLogIfModified))


class AwsServiceInterface(metaclass=AwsServiceInterfaceMetaClass):

    def uploadExperimentFilesOnInterval(self, scanNumber, guidedSetupForm):
        """ Uploads the summary csv for the experiment. """

    def uploadFinalExperimentFiles(self, guidedSetupForm):
        """ Uploads the summary csv for the experiment. """

    def uploadExperimentLog(self):
        """ Uploads the log file for the experiment. """

    def uploadIssueLog(self):
        """ Uploads the issue log to AWS in the experiment folder. """

    def downloadIssueLogIfModified(self, lastDownloaded):
        """ Downloads the issue log for the experiment, if modified since `lastDownloaded`. """

