class GlobalFileManager:
    def __init__(self, mainSavePath):
        self.mainSavePath = mainSavePath
        self.summaryAnalyzed = rf"{mainSavePath}/summaryAnalyzed.csv"
        self.remoteSummaryAnalyzed = rf"{mainSavePath}/remoteSummaryAnalyzed.csv"
        self.setupForm = rf"{mainSavePath}/setupForm.png"
        self.summaryPdf = rf"{mainSavePath}/Summary.pdf"
        self.issueLog = rf"{mainSavePath}/Issue Log.json"

    def getSummaryAnalyzed(self):
        return self.summaryAnalyzed

    def getRemoteSummaryAnalyzed(self):
        return self.remoteSummaryAnalyzed

    def getSetupForm(self):
        return self.setupForm

    def getSummaryPdf(self):
        return self.summaryPdf

    def getSavePath(self):
        return self.mainSavePath

    def getIssueLog(self):
        return self.issueLog
