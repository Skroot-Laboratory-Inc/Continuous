import datetime
import json
from typing import List

from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.helper.helper_functions import datetimeToMillis
from src.app.helper.run_on_interval import RunOnInterval
from src.app.main_shared.service.aws_service_interface import AwsServiceInterface
from src.app.model.issue.issue import Issue
from src.app.model.issue.timestamped_message import TimestampedMessage
from src.app.properties.aws_properties import AwsProperties
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager


class IssueLog:
    def __init__(self, rootManager: RootManager, awsService: AwsServiceInterface, globalFileManager: GlobalFileManager):
        self.RootManager = rootManager
        self.lastUpdatedTime = datetime.datetime.now()
        self.issues = []
        self.openIssues = []
        self.resolvedIssues = []
        self.nextIssueId = 1
        self.AwsService = awsService
        self.GlobalFileManager = globalFileManager
        self.Colors = Colors()
        self.fonts = FontTheme()
        self.syncFromS3()
        self.lastDownloaded = datetime.datetime.now(datetime.timezone.utc)
        self.CheckIssuesInterval = RunOnInterval(
            self.syncFromS3,
            AwsProperties().issueLogDownloadRate*60,
            120
        )
        self.CheckIssuesInterval.startFn()

    def createIssue(self, issueTitle):
        self.syncFromS3()
        if issueTitle is not None:
            issue = Issue(
                self.nextIssueId,
                issueTitle,
                False,
                [TimestampedMessage(datetimeToMillis(datetime.datetime.now()), "Issue opened by operator.")])
            self.issues.append(issue)
            self.openIssues = [issue for issue in self.issues if issue.resolved is not True]
            self.resolvedIssues = [issue for issue in self.issues if issue.resolved is True]
            self.syncToS3()
            return issue
        return None

    def updateIssue(self, issue: Issue):
        self.syncFromS3()
        self.issues = self.findAndReplace(self.issues, issue)
        self.syncToS3()

    def syncFromS3(self):
        try:
            self.downloadIssueLogIfModified()
            with open(self.GlobalFileManager.getIssueLog()) as issueLog:
                issuesJson = json.load(issueLog)
            self.nextIssueId = max([int(issue.issueId) for issue in self.issues]) + 1
        except:
            self.nextIssueId = 1
        return self.issues

    def syncToS3(self):
        with open(self.GlobalFileManager.getIssueLog(), "w") as issueLog:
            issueLog.write(json.dumps(self.jsonFromIssues(self.issues)))
        self.AwsService.uploadIssueLog()
        self.lastDownloaded = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=10)

    def downloadIssueLogIfModified(self):
        self.lastDownloaded = self.AwsService.downloadIssueLogIfModified(self.lastDownloaded)

    def clear(self):
        self.CheckIssuesInterval.stopFn()
        self.issues = []
        self.nextIssueId = 1

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
