import os

from src.app.file_manager.common_file_manager import CommonFileManager


class AwsProperties:
    def __init__(self):
        self.csvUploadRate = 60  # Minutes
        self.notesUploadRate = 60  # Minutes
