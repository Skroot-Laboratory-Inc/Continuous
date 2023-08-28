import tkinter as tk

from analysis import Analysis


class ExperimentNotes:
    def __init__(self, readerNumber):
        self.readerNumber = readerNumber
        self.notes = ''
        self.notesTimestamps = []

    def addExperimentNotesMenubar(self, menu):
        menu.add_command(label=f"Reader {self.readerNumber}", command=lambda: self.typeExperimentNotes())

    def typeExperimentNotes(self):
        newNotes = tk.simpledialog.askstring(f'Reader {self.readerNumber} notes',
                                             f'Add any experiment notes for {self.readerNumber} here. \nThey can be viewed in the pdf generated.')
        self.updateExperimentNotes(newNotes)

    def updateExperimentNotes(self, newNotes):
        if newNotes != '':
            if not self.time:
                timestamp = 0
            else:
                timestamp = round(self.time[-1], 4)
            self.notesTimestamps.append(timestamp)
            if self.notes == '':
                self.notes = f'{self.notes}{round(timestamp, 2)} hrs: {newNotes}'
            else:
                self.notes = f'{self.notes}\n{round(timestamp, 2)} hrs: {newNotes}'
            with open(f'{self.savePath}/notes.txt', 'w') as f:
                f.write(self.notes)
            self.sendToServer(f'{self.savePath}/notes.txt')

    def addNotesToPdf(self, pdf, currentX, currentY, notesWidth, notesLineHeight, plotHeight, paddingY):
        currentY += plotHeight / 8
        pdf.placeText(self.notes, currentX, currentY, notesWidth, notesLineHeight, 10, False)
        currentY += (7 * plotHeight) / 8
        currentX += notesWidth
        currentY += paddingY
        return currentX, currentY
