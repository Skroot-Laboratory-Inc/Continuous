from typing import List

from src.app.model.issue.issue_message import IssueMessage


class Issue:
    def __init__(self, issueId: str,  title: str, resolved: bool, messages: List[IssueMessage]):
        self.issueId = issueId
        self.title = title
        self.messages = messages
        self.resolved = resolved

    def asJson(self):
        return {
            "issueId": self.issueId,
            "messages": self.messages,
            "title": self.title,
            "resolved": self.resolved,
        }

