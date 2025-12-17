from typing import Callable

from src.app.helper_methods.model.issue.issue import Issue


class PotentialIssue:
    def __init__(self, requiredConsecutiveProblem: int, issueMessage: str, createIssueFn: Callable[[str], Issue]):
        self.issueMessage = issueMessage
        self.createIssueFn = createIssueFn
        self.consecutiveProblem = 1
        self.requiredConsecutiveProblem = requiredConsecutiveProblem
        self.resolved = False

    def confirmIssue(self):
        return self.createIssueFn(self.issueMessage)

    def persistIssue(self):
        self.consecutiveProblem += 1
        if self.consecutiveProblem >= self.requiredConsecutiveProblem:
            return self.confirmIssue()
        else:
            return self

    def resolveIssue(self):
        self.consecutiveProblem = 0

