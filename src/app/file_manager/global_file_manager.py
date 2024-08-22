class GlobalFileManager:
    def __init__(self, mainSavePath):
        self.mainSavePath = mainSavePath
        self.summaryAnalyzed = rf"{mainSavePath}/summaryAnalyzed.csv"
        self.summaryFigure = rf"{mainSavePath}/Summary Figure.jpg"
        self.setupForm = rf"{mainSavePath}/setupForm.png"
        self.summaryPdf = rf"{mainSavePath}/Summary.pdf"
        self.experimentNotesTxt = f'{mainSavePath}/notes.txt'
        self.experimentMetadata = f'{mainSavePath}/metadata.json'

    def getSummaryAnalyzed(self):
        return self.summaryAnalyzed

    def getSummaryFigure(self):
        return self.summaryFigure

    def getSetupForm(self):
        return self.setupForm

    def getSummaryPdf(self):
        return self.summaryPdf

    def getSavePath(self):
        return self.mainSavePath

    def getExperimentNotesTxt(self):
        return self.experimentNotesTxt

    def getExperimentMetadata(self):
        return self.experimentMetadata

