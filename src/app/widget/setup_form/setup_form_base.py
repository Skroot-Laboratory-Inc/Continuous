"""Base class for Setup forms that configure reader runs."""
from abc import ABC, abstractmethod
from typing import Tuple

from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.model.setup_reader_form_input import SetupReaderFormInput


class SetupReaderForm(ABC):
    """Abstract base class for Setup forms across different use cases."""

    @abstractmethod
    def getConfiguration(self) -> Tuple[SetupReaderFormInput, GlobalFileManager]:
        """
        Get the current configuration.

        Returns:
            Tuple of (SetupReaderFormInput, GlobalFileManager)
        """
        pass

    @abstractmethod
    def setCalibrate(self):
        """Update the calibration setting based on user input."""
        pass

    @abstractmethod
    def onCancel(self):
        """Handle cancel button click."""
        pass

    @abstractmethod
    def updateConfiguration(self) -> SetupReaderFormInput:
        """
        Update and reset the configuration for a new run.

        Returns:
            Updated SetupReaderFormInput
        """
        pass

    @abstractmethod
    def onSubmit(self):
        """Handle submit button click and validate inputs."""
        pass

    @abstractmethod
    def createSavePath(self, date: str) -> str:
        """
        Create a unique save path for the run data.

        Args:
            date: The date string for the run

        Returns:
            The full save path
        """
        pass

    def resetFlowRate(self) -> SetupReaderFormInput:
        """
        Reset the flow rate to default value.

        This is a no-op for UseCases that don't use pumps.
        Override in subclasses that require pump flow rate management.

        Returns:
            Updated SetupReaderFormInput (default: returns current configuration)
        """
        config, _ = self.getConfiguration()
        return config
