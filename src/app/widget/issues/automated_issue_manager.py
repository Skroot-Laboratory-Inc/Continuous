import datetime
import json
from typing import List

from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.helper.helper_functions import datetimeToMillis
from src.app.model.issue.issue import Issue
from src.app.model.issue.timestamped_message import TimestampedMessage
from src.app.reader.service.aws_service_interface import AwsServiceInterface


class AutomatedIssueManager:
    def __init__(self, awsService: AwsServiceInterface, globalFileManager: GlobalFileManager):
        self.issues = []
        self.nextIssueId = 1
        self.AwsService = awsService
        self.GlobalFileManager = globalFileManager

    def createIssue(self, issueTitle):
        if issueTitle is not None:
            issue = Issue(
                self.nextIssueId,
                issueTitle,
                False,
                [TimestampedMessage(datetimeToMillis(datetime.datetime.now()), "Issue opened by operator.")])
            self.issues.append(issue)
            self.syncToS3()
            return issue
        return None

    def updateIssue(self, issue: Issue):
        self.issues = self.findAndReplace(self.issues, issue)
        self.syncToS3()

    def syncToS3(self):
        with open(self.GlobalFileManager.getIssueLog(), "w") as issueLog:
            issueLog.write(json.dumps(self.jsonFromIssues(self.issues)))
        self.AwsService.uploadIssueLog()

    @staticmethod
    def jsonFromIssues(issues):
        jsonIssues = [issue.asJson() for issue in issues]
        return {
            "issueLog": jsonIssues
        }

    @staticmethod
    def findAndReplace(items: List[Issue], newItem: Issue) -> List[Issue]:
        for item in items:
            if item.issueId == newItem.issueId:
                items.remove(item)
                items.append(newItem)
                return items
