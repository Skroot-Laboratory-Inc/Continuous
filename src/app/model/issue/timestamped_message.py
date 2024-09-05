class TimestampedMessage:
    def __init__(self, timestamp: int, entry: str):
        self.timestamp = timestamp
        self.entry = entry

    def asJson(self):
        return {
            self.timestamp: self.entry
        }

