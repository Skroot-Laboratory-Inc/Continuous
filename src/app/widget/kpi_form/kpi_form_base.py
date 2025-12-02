"""Base class for KPI forms that display reader information."""
from abc import ABC, abstractmethod
from typing import Optional


class KpiForm(ABC):
    """Abstract base class for KPI forms across different use cases."""

    @abstractmethod
    def setConstants(self, lotId: str, user: str, pumpFlowRate: Optional[float]):
        """
        Set the constant values for the KPI form.

        Args:
            lotId: The lot/run ID
            user: The user who started the run
            pumpFlowRate: The pump flow rate to reset the form to (if applicable)
        """
        pass

    @abstractmethod
    def setSaturation(self, saturationDate: int):
        """
        Set the saturation date/time.

        Args:
            saturationDate: Saturation timestamp in milliseconds
        """
        pass

    @abstractmethod
    def setSgi(self, sgi: float):
        """
        Set the current SGI value.

        Args:
            sgi: The SGI (Specific Growth Index) value
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
