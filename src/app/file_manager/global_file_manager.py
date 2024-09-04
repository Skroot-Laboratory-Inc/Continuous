class GlobalFileManager:
    def __init__(self, mainSavePath):
        self.mainSavePath = mainSavePath
        self.summaryAnalyzed = rf"{mainSavePath}/summaryAnalyzed.csv"
        self.remoteSummaryAnalyzed = rf"{mainSavePath}/remoteSummaryAnalyzed.csv"
        self.summaryFigure = rf"{mainSavePath}/Summary Figure.jpg"
        self.setupForm = rf"{mainSavePath}/setupForm.png"
        self.summaryPdf = rf"{mainSavePath}/Summary.pdf"
        self.issueLog = rf"{mainSavePath}/Issue Log.json"
        self.experimentNotesTxt = f'{mainSavePath}/notes.txt'
        self.experimentMetadata = f'{mainSavePath}/metadata.json'

    def getSummaryAnalyzed(self):
        return self.summaryAnalyzed

    def getRemoteSummaryAnalyzed(self):
        return self.remoteSummaryAnalyzed

    def getSummaryFigure(self):
        return self.summaryFigure

    def getSetupForm(self):
        return self.setupForm

    def getSummaryPdf(self):
        return self.summaryPdf

    def getSavePath(self):
        return self.mainSavePath

    def getIssueLog(self):
        return self.issueLog

    def getExperimentNotesTxt(self):
        return self.experimentNotesTxt

    def getExperimentMetadata(self):
        return self.experimentMetadata

