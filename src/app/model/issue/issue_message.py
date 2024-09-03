class IssueMessage:
    def __init__(self, timestamp: str, entry: str):
        self.timestamp = timestamp
        self.entry = entry

    def asJson(self):
        return {
            self.timestamp: self.entry
        }

