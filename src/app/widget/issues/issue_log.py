import json
from datetime import datetime
from tkinter import ttk
from typing import List

from src.app.buttons.view_issue_button import ViewIssueButton
from src.app.file_manager.common_file_manager import CommonFileManager
from src.app.file_manager.global_file_manager import GlobalFileManager
from src.app.helper.helper_functions import formatDateTime
from src.app.main_shared.service.aws_service_interface import AwsServiceInterface
from src.app.model.issue.issue import Issue
from src.app.model.issue.issue_message import IssueMessage
from src.app.properties.gui_properties import GuiProperties
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.issues.view_issue import ViewIssuePopup

import tkinter as tk
from PIL import Image, ImageTk


class IssueLog:
    def __init__(self, rootManager: RootManager, awsService: AwsServiceInterface, globalFileManager: GlobalFileManager):
        self.lastUpdatedTime = datetime.now()
        self.issues = []
        self.openIssues = []
        self.resolvedIssues = []
        self.nextIssueId = 1
        self.AwsService = awsService
        self.RootManager = rootManager
        self.GlobalFileManager = globalFileManager
        self.Colors = Colors()
        self.issueLogFrame = self.RootManager.createPaddedFrame(self.Colors.secondaryColor)
        self.issueLogFrame.grid_columnconfigure(0, weight=9)
        self.issueLogFrame.grid_columnconfigure(1, weight=1, minsize=35)
        self.issueLogFrame.grid_columnconfigure(2, weight=1, minsize=35)
        self.fonts = FontTheme()
        commonFileManager = CommonFileManager()
        image = Image.open(commonFileManager.getAddIcon())
        resizedImage = image.resize((35, 35), Image.LANCZOS)
        self.createIcon = ImageTk.PhotoImage(resizedImage)
        image = Image.open(commonFileManager.getRefreshIcon())
        resizedImage = image.resize((35, 35), Image.LANCZOS)
        self.refreshIcon = ImageTk.PhotoImage(resizedImage)
        self.syncFromS3()
        self.populateUi()

    def populateUi(self):
        for widget in self.issueLogFrame.winfo_children():
            widget.destroy()
        row = 0
        row = self.showOpenIssues(row)
        self.showResolvedIssues(row)

    def updateLastUpdated(self):
        self.lastUpdatedTime = datetime.now()
        try:
            self.lastUpdatedLabel.configure(text=f'Last Updated: {formatDateTime(self.lastUpdatedTime)}')
        except:
            pass

    def showOpenIssues(self, row):
        self.lastUpdatedLabel = tk.Label(
            self.issueLogFrame,
            text=f'Last Updated: {formatDateTime(self.lastUpdatedTime)}',
            bg='white',
            font=self.fonts.footnote)
        self.lastUpdatedLabel.grid(row=row, column=0, columnspan=3, sticky='e', pady=(0, 5))
        row += 1

        headerLabel = tk.Label(
            self.issueLogFrame,
            text=f'Open Issues ({len(self.openIssues)}):',
            bg='white',
            font=self.fonts.header1)
        headerLabel.grid(row=row, column=0)
        refreshButton = tk.Button(
            self.issueLogFrame,
            bg=self.Colors.secondaryColor,
            highlightthickness=0,
            borderwidth=0,
            image=self.refreshIcon,
            command=lambda: self.syncFromS3())
        refreshButton.grid(row=row, column=1)
        createButton = tk.Button(
            self.issueLogFrame,
            bg=self.Colors.secondaryColor,
            highlightthickness=0,
            borderwidth=0,
            image=self.createIcon,
            command=lambda: self.createIssue())
        createButton.grid(row=row, column=2)
        row += 1

        row = self.createSeparatorLine(self.issueLogFrame, row)

        for issue in sorted(self.openIssues, key=lambda i: i.issueId):
            button = ViewIssueButton(
                self.issueLogFrame,
                self.viewIssue,
                issue,
            ).viewIssueButton
            button.grid(row=row, column=0, pady=15)
            row += 1
        return row

    def showResolvedIssues(self, row):
        headerLabel = tk.Label(
            self.issueLogFrame,
            text=f'Resolved Issues ({len(self.resolvedIssues)}):',
            bg='white',
            font=self.fonts.header1)
        headerLabel.grid(row=row, column=0)
        row += 1

        row = self.createSeparatorLine(self.issueLogFrame, row)

        for issue in sorted(self.resolvedIssues, key=lambda i: i.issueId):
            button = ViewIssueButton(
                self.issueLogFrame,
                self.viewIssue,
                issue,
            ).viewIssueButton
            button.grid(row=row, column=0, pady=15)
            row += 1
        return row

    def viewIssue(self, issue: Issue):
        ViewIssuePopup(self.RootManager, issue, self.updateIssue)

    def createIssue(self):
        self.syncFromS3()
        issueTitle = tk.simpledialog.askstring(
            f'Report An Issue',
            f'Enter a title for the issue here. The ID for this issue will be Issue {self.nextIssueId}',

        )
        if issueTitle is not None:
            issue = Issue(
                f"{self.nextIssueId}",
                issueTitle,
                False,
                [IssueMessage(formatDateTime(datetime.now()), "Issue opened.")])
            self.issues.append(issue)
            self.openIssues = [issue for issue in self.issues if issue.resolved is not True]
            self.resolvedIssues = [issue for issue in self.issues if issue.resolved is True]
            self.syncToS3()

    def updateIssue(self, issue: Issue):
        self.syncFromS3()
        self.issues = self.findAndReplace(self.issues, issue)
        self.openIssues = [issue for issue in self.issues if issue.resolved is not True]
        self.resolvedIssues = [issue for issue in self.issues if issue.resolved is True]
        self.syncToS3()

    def syncFromS3(self):
        self.updateLastUpdated()
        try:
            self.AwsService.downloadIssueLog()
            with open(self.GlobalFileManager.getIssueLog()) as issueLog:
                issuesJson = json.load(issueLog)
                self.issues = [self.issueFromJson(issue) for issue in issuesJson["issueLog"]]
            self.openIssues = [issue for issue in self.issues if issue.resolved is not True]
            self.resolvedIssues = [issue for issue in self.issues if issue.resolved is True]
            self.nextIssueId = max([int(issue.issueId) for issue in self.issues]) + 1
        except:
            self.openIssues = 1
            self.openIssues = []
            self.resolvedIssues = []
            self.nextIssueId = 1

    def syncToS3(self):
        self.populateUi()
        with open(self.GlobalFileManager.getIssueLog(), "w") as issueLog:
            issueLog.write(json.dumps(self.jsonFromIssues(self.issues)))
        self.AwsService.uploadIssueLog()
        pass

    def placeIssueLog(self):
        guiProperties = GuiProperties()
        self.issueLogFrame.place(
            relx=0.67,
            rely=guiProperties.readerPlotRelY,
            relwidth=0.33,
            relheight=guiProperties.readerPlotHeight / 2)

    def issueFromJson(self, jsonIssue):
        return Issue(
            jsonIssue["issueId"],
            jsonIssue["title"],
            jsonIssue["resolved"],
            self.issueMessageFromJson(jsonIssue["messages"])
        )

    def clear(self):
        for widgets in self.issueLogFrame.winfo_children():
            widgets.destroy()

    @staticmethod
    def jsonFromIssues(issues):
        jsonIssues = [issue.asJson() for issue in issues]
        return {
            "issueLog": jsonIssues
        }

    @staticmethod
    def issueMessageFromJson(jsonMessage):
        messages = []
        for m in jsonMessage:
            for timestamp, message in m.items():
                messages.append(IssueMessage(timestamp, message))
        return messages

    @staticmethod
    def findAndReplace(items: List[Issue], newItem: Issue) -> List[Issue]:
        for item in items:
            if item.issueId == newItem.issueId:
                items.remove(item)
                items.append(newItem)
                return items

    @staticmethod
    def createSeparatorLine(window, row):
        ttk.Separator(window, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky='ew')
        row += 1
        return row
