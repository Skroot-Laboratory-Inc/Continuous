class GlobalFileManager:
    def __init__(self, mainSavePath):
        self.mainSavePath = mainSavePath
        self.summaryAnalyzed = rf"{mainSavePath}/summaryAnalyzed.csv"
        self.summaryFigure = rf"{mainSavePath}/Summary Figure.jpg"
        self.setupForm = rf"{mainSavePath}/setupForm.png"
        self.summaryPdf = rf"{mainSavePath}/Summary.pdf"

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

