import unittest

from src.app.widget import release_notes


class TestReleaseNotesMethods(unittest.TestCase):

    def test_sortNotes(self):
        correctlySortedReleaseNotes = {
            "v2.0.0": "notes2.0.0",
            "v1.12.0": "notes1.12.0",
            "v1.2.0": "notes1.2.0",
            "v1.0.12": "notes1.0.12",
            "v1.0.2": "notes1.0.2",
            "v1.0.0": "notes1.0.0",
        }
        unsortedReleaseNotes = {
            "v1.0.0": "notes1.0.0",
            "v1.0.12": "notes1.0.12",
            "v1.0.2": "notes1.0.2",
            "v1.12.0": "notes1.12.0",
            "v1.2.0": "notes1.2.0",
            "v2.0.0": "notes2.0.0"
        }

        sortedReleaseNotes = release_notes.sortNotes(unsortedReleaseNotes)

        correctlySortedReleaseNotesKeys = correctlySortedReleaseNotes.keys()
        sortedReleaseNotesKeys = list(sortedReleaseNotes.keys())
        for correctIndex, correctVersion in enumerate(correctlySortedReleaseNotesKeys):
            self.assertEqual(correctIndex, sortedReleaseNotesKeys.index(correctVersion))

        # Check that the actual dictionary is the same (the notes are attached to the correct version)
        self.assertDictEqual(correctlySortedReleaseNotes, sortedReleaseNotes)


if __name__ == '__main__':
    unittest.main()
