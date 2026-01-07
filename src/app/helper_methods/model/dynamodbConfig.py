from datetime import datetime

from src.app.helper_methods.datetime_helpers import datetimeToMillis


class DynamodbConfig:
    def __init__(self, endDate: int = None, startDate: int = None, saturationDate: int = None, lotId: str = "", incubator: str = "", flagged: bool = False, warehouse: str = ""):
        self.endDate = endDate
        self.startDate = startDate
        self.saturationDate = saturationDate
        self.lotId = lotId
        self.incubator = incubator
        self.flagged = flagged
        self.warehouse = warehouse

    def asTags(self):
        return {
                    "end_date": self.endDate,
                    "start_date": self.startDate,
                    "lot_id": self.lotId,
                    "incubator": self.incubator,
                    "saturation_date": self.saturationDate,
                    "flagged": self.flagged,
                    "warehouse": self.warehouse,
                }

    def softEquals(self, other):
        """ This compares the object ignoring the volatile attribute (saturationDate). """
        if not isinstance(other, DynamodbConfig):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.endDate == other.endDate and
                self.startDate == other.startDate and
                self.lotId == other.lotId and
                self.incubator == other.incubator and
                self.flagged == other.flagged and
                self.warehouse == other.warehouse)

    def __eq__(self, other):
        if not isinstance(other, DynamodbConfig):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.endDate == other.endDate and
                self.startDate == other.startDate and
                self.saturationDate == other.saturationDate and
                self.lotId == other.lotId and
                self.incubator == other.incubator and
                self.flagged == other.flagged and
                self.warehouse == other.warehouse)
