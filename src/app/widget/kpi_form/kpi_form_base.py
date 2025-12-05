"""Base class for KPI forms that display reader information."""
import tkinter as tk
from abc import ABC, abstractmethod

from reactivex import Subject

from src.app.helper_methods.datetime_helpers import formatDatetime, millisToDatetime
from src.app.widget.sidebar.configurations.secondary_axis_type import SecondaryAxisType
from src.app.widget.sidebar.configurations.secondary_axis_units import SecondaryAxisUnits


class KpiForm(ABC):
    """Abstract base class for KPI forms across different use cases."""

    def __init__(self):
        self._saturationDate = None
        self._sgi = tk.StringVar(value="-")
        self._saturationTime = tk.StringVar(value="")
        self._runId = tk.StringVar()
        self._user = tk.StringVar()
        self._axisLabel = tk.StringVar(value=f"{SecondaryAxisType().getConfig()} {SecondaryAxisUnits().getAsUnit()}:")
        self._secondaryAxisData = tk.StringVar(value="")
        self._lastSecondAxisEntry = Subject()

    @abstractmethod
    def setConstants(self, lotId: str, user: str):
        """
        Set the constant values for the KPI form.

        Args:
            lotId: The lot/run ID
            user: The user who started the run
        """
        pass

    @abstractmethod
    def resetForm(self):
        """Reset the form to its initial state."""
        pass

    @abstractmethod
    def submitSecondaryAxisData(self, data: str):
        """
        Submit secondary axis data.

        Args:
            data: The secondary axis data value
        """
        pass

    @abstractmethod
    def export(self):
        """Export the current run data."""
        pass

    @property
    def saturationDate(self):
        """Gets the saturation date displayed on the KPI form."""
        return self._saturationDate

    @saturationDate.setter
    def saturationDate(self, value: int):
        """Sets the saturation date displayed on the KPI form."""
        self._saturationDate = value
        self._saturationTime.set(formatDatetime(millisToDatetime(value)))

    @property
    def sgi(self):
        """Gets the saturation date displayed on the KPI form."""
        return self._sgi

    @property
    def lastSecondAxisEntry(self):
        """Gets the saturation date displayed on the KPI form."""
        return self._lastSecondAxisEntry

    @sgi.setter
    def sgi(self, value: float):
        """Sets the saturation date displayed on the KPI form."""
        self._sgi.set(f"{round(value, 1)}")
