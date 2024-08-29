import json
import tkinter as tk

from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.model.result_set.result_set import ResultSet


class ExperimentNotes:
    def __init__(self, FileManager: GlobalFileManager):
        self.notes = {"All Vessels": []}
        self.notesTimestamps = {}
        self.FileManager = FileManager

    def typeExperimentNotes(self, readerNumber, resultSet: ResultSet):
        newNotes = tk.simpledialog.askstring(
            f'Reader {readerNumber} notes',
            f'Add any experiment notes for {readerNumber} here. '
            f'\nThey can be viewed in the pdf generated.')
        self.updateExperimentNotes(readerNumber, newNotes, resultSet)

    def updateExperimentNotes(self, readerNumber, newNotes, resultSet: ResultSet):
        if newNotes != '':
            timestamp = 0
            if resultSet.getTime():
                timestamp = round(resultSet.getTime()[-1], 4)

            key = "All Vessels"
            if readerNumber != 0:
                key = f"Vessel {readerNumber}"

            try:
                existingNotes = self.notes[key]
                existingTimestamps = self.notesTimestamps[key]
            except:
                existingNotes = []
                existingTimestamps = []

            existingTimestamps.append(timestamp)
            self.notesTimestamps[key] = existingTimestamps
            existingNotes.append({"timestamp": round(timestamp, 2), "entry": newNotes})
            self.notes[key] = existingNotes

            with open(self.FileManager.getExperimentNotesTxt(), 'w') as f:
                f.write(self.toString())
            with open(self.FileManager.getExperimentMetadata(), 'w') as f:
                json.dump(self.toJson(), f, indent=None)

    def getTimestamps(self, readerNumber):
        try:
            readerTimestamps = self.notesTimestamps[f"Vessel {readerNumber}"]
        except:
            readerTimestamps = []
        try:
            allTimestamps = self.notesTimestamps["All Vessels"]
        except:
            allTimestamps = []
        return readerTimestamps + allTimestamps

    def toJson(self):
        return {"Notes": self.notes}

    def toString(self) -> str:
        notesString = ''
        for vesselLabel, allVesselNotes in self.notes.items():
            notesString = f"{notesString}\n\n{vesselLabel}"
            for noteEntry in allVesselNotes:
                notesString = f"{notesString}\n{noteEntry['timestamp']}: {noteEntry['entry']}"
        return notesString
