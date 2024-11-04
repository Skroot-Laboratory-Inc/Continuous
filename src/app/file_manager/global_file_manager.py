class GlobalFileManager:
    def __init__(self, mainSavePath):
        self.mainSavePath = mainSavePath
        self.issueLog = rf"{mainSavePath}/Issue Log.json"

    def getSavePath(self):
        return self.mainSavePath

    def getIssueLog(self):
        return self.issueLog
