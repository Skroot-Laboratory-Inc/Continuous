import json
from datetime import datetime
from tkinter import simpledialog

from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.helper.helper_functions import datetimeToMillis
from src.app.model.issue.timestamped_message import TimestampedMessage
from src.app.model.result_set.result_set import ResultSet


class ExperimentNotes:
    def __init__(self, FileManager: GlobalFileManager):
        self.notesTimes = {"All Vessels": []}
        self.notesTimestamps = {}
        self.FileManager = FileManager

    def reset(self):
        self.notesTimes = {"All Vessels": []}
        self.notesTimestamps = {}

    def typeExperimentNotes(self, readerNumber, resultSet: ResultSet):
        newNotes = simpledialog.askstring(
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
                existingNotes = self.notesTimes[key]
                existingTimestamps = self.notesTimestamps[key]
            except:
                existingNotes = []
                existingTimestamps = []

            existingNotes.append({time: newNotes})
            self.notesTimes[key] = existingNotes
            existingTimestamps.append(TimestampedMessage(datetimeToMillis(datetime.now()), newNotes).asJson())
            self.notesTimestamps[key] = existingTimestamps

            with open(self.FileManager.getExperimentNotesTxt(), 'w') as f:
                f.write(self.toString())
            with open(self.FileManager.getExperimentMetadata(), 'w') as f:
                json.dump(self.toJson(), f, indent=None)

    def getTimes(self, readerNumber):
        """ Used for the plotter to create vertical lines at each note. """
        times = []
        for vesselLabel, allVesselNotes in self.notesTimes.items():
            if vesselLabel == f"Vessel {readerNumber}" or vesselLabel == "All Vessels":
                for entry in allVesselNotes:
                    for notesTime, notesEntry in entry.items():
                        times.append(notesTime)
        return times

    def toJson(self):
        return {"Notes": self.notesTimestamps}

    def toString(self) -> str:
        notesString = ''
        for vesselLabel, allVesselNotes in self.notesTimes.items():
            notesString = f"{notesString}\n\n{vesselLabel}"
            for entry in allVesselNotes:
                for notesTimestamp, notesEntry in entry.items():
                    notesString = f"{notesString}\n{notesTimestamp}: {notesEntry}"
        return notesString
