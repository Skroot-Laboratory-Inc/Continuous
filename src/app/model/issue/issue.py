from typing import List

from src.app.model.issue.timestamped_message import TimestampedMessage


class Issue:
    def __init__(self, issueId: str, title: str, resolved: bool, messages: List[TimestampedMessage]):
        self.issueId = issueId
        self.title = title
        self.resolved = resolved
        self.messages = messages

    def asJson(self):
        return {
            "id": self.issueId,
            "messages": [message.asJson() for message in self.messages],
            "title": self.title,
            "resolved": self.resolved,
        }

