import json
import tkinter as tk
from datetime import datetime

from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.helper.helper_functions import formatDateTime
from src.app.model.result_set.result_set import ResultSet


class ExperimentNotes:
    def __init__(self, FileManager: GlobalFileManager):
        self.notes = {"All Vessels": []}
        self.FileManager = FileManager

    def typeExperimentNotes(self, readerNumber, resultSet: ResultSet):
        newNotes = tk.simpledialog.askstring(
            f'Reader {readerNumber} notes',
            f'Add any experiment notes for {readerNumber} here. '
            f'\nThey can be viewed in the pdf generated.')
        self.updateExperimentNotes(readerNumber, newNotes, resultSet)

    def updateExperimentNotes(self, readerNumber, newNotes, resultSet: ResultSet):
        if newNotes != '':
            time = 0
            if resultSet.getTime():
                time = round(resultSet.getTime()[-1], 4)

            key = "All Vessels"
            if readerNumber != 0:
                key = f"Vessel {readerNumber}"

            try:
                existingNotes = self.notes[key]
            except:
                existingNotes = []

            existingNotes.append({"time": round(time, 2), "timestamp": formatDateTime(datetime.now()), "entry": newNotes})
            self.notes[key] = existingNotes

            with open(self.FileManager.getExperimentNotesTxt(), 'w') as f:
                f.write(self.toString())
            with open(self.FileManager.getExperimentMetadata(), 'w') as f:
                json.dump(self.toJson(), f, indent=None)

    def getTimes(self, readerNumber):
        """ Used for the plotter to create vertical lines at each note. """
        times = []
        for vesselLabel, allVesselNotes in self.notes.items():
            if vesselLabel == f"Vessel {readerNumber}" or vesselLabel == "All Vessels":
                for noteEntry in allVesselNotes:
                    times.append(noteEntry['time'])
        return times

    def toJson(self):
        return {"Notes": self.notes}

    def toString(self) -> str:
        notesString = ''
        for vesselLabel, allVesselNotes in self.notes.items():
            notesString = f"{notesString}\n\n{vesselLabel}"
            for noteEntry in allVesselNotes:
                notesString = f"{notesString}\n{noteEntry['time']}: {noteEntry['entry']}"
        return notesString
