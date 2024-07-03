import tkinter as tk

from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.model.result_set import ResultSet


class ExperimentNotes:
    def __init__(self, readerNumber, FileManager: ReaderFileManager):
        self.readerNumber = readerNumber
        self.notes = ''
        self.notesTimestamps = []
        self.FileManager = FileManager

    def typeExperimentNotes(self, resultSet: ResultSet):
        newNotes = tk.simpledialog.askstring(f'Reader {self.readerNumber} notes',
                                             f'Add any experiment notes for {self.readerNumber} here. \nThey can be viewed in the pdf generated.')
        self.updateExperimentNotes(newNotes, resultSet)

    def updateExperimentNotes(self, newNotes, resultSet: ResultSet):
        if newNotes != '':
            if not resultSet.getTime():
                timestamp = 0
            else:
                timestamp = round(resultSet.getTime()[-1], 4)
            self.notesTimestamps.append(timestamp)
            if self.notes == '':
                self.notes = f'{self.notes}{round(timestamp, 2)} hrs: {newNotes}'
            else:
                self.notes = f'{self.notes}\n{round(timestamp, 2)} hrs: {newNotes}'
            with open(self.FileManager.getExperimentNotes(), 'w') as f:
                f.write(self.notes)

    def addNotesToPdf(self, pdf, currentX, currentY, notesWidth, notesLineHeight, plotHeight, paddingY):
        currentY += plotHeight / 8
        pdf.placeText(self.notes, currentX, currentY, notesWidth, notesLineHeight, 10, False)
        currentY += (7 * plotHeight) / 8
        currentX += notesWidth
        currentY += paddingY
        return currentX, currentY
