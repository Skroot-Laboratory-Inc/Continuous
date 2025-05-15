from datetime import datetime
from typing import List

from src.app.helper_methods.datetime_helpers import datetimeToMillis
from src.app.model.issue.timestamped_message import TimestampedMessage


class Issue:
    def __init__(self, issueId: int, title: str, resolved: bool, messages: List[TimestampedMessage]):
        self.issueId = issueId
        self.title = title
        self.resolved = resolved
        self.messages = messages

    def resolveIssue(self):
        self.resolved = True
        self.messages.append(TimestampedMessage(datetimeToMillis(datetime.now()), "Marked as resolved by operator."))
        return self

    def asJson(self):
        return {
            "id": self.issueId,
            "messages": [message.asJson() for message in self.messages],
            "title": self.title,
            "resolved": self.resolved,
        }

