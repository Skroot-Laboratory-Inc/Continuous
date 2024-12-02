import os
import unittest

from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.file_manager.reader_file_manager import ReaderFileManager
from src.app.reader.service.aws_service import AwsService
from src.app.widget.issues.automated_issue_manager import AutomatedIssueManager


class TestIssueManager(unittest.TestCase):
    def test_noOpenIssues(self):
        """
        Test that no open issues are found when there are no issues present
        """
        globalFileManager = GlobalFileManager("test")
        readerFileManager = ReaderFileManager("test", 1)
        awsService = AwsService(readerFileManager, globalFileManager)
        awsService.AwsBoto3Service.disabled = True

        self.assertEqual(
            AutomatedIssueManager(awsService, globalFileManager).hasOpenIssues(),
            False
        )

    def test_hasOpenIssues(self):
        """
        Test that resolved issues do not mark the experiment as flagged
        """
        if not os.path.exists("./temp"):
            os.mkdir("./temp")
        globalFileManager = GlobalFileManager("./temp")
        readerFileManager = ReaderFileManager("test", 1)
        awsService = AwsService(readerFileManager, globalFileManager)
        awsService.AwsBoto3Service.disabled = True
        issueManager = AutomatedIssueManager(awsService, globalFileManager)
        issueManager.createIssue("has issues")
        issueManager.issues[0].resolved = True
        os.remove("./temp/Issue Log.json")

        self.assertEqual(
            issueManager.hasOpenIssues(),
            False
        )

    def test_hasResolvedIssues(self):
        """
        Test resolved issues
        """
        if not os.path.exists("./temp"):
            os.mkdir("./temp")
        globalFileManager = GlobalFileManager("./temp")
        readerFileManager = ReaderFileManager("test", 1)
        awsService = AwsService(readerFileManager, globalFileManager)
        awsService.AwsBoto3Service.disabled = True
        issueManager = AutomatedIssueManager(awsService, globalFileManager)
        issueManager.createIssue("has issues")
        os.remove("./temp/Issue Log.json")

        self.assertEqual(
            issueManager.hasOpenIssues(),
            True
        )


if __name__ == '__main__':
    unittest.main()
