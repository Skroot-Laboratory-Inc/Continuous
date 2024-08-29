import json
from tkinter import ttk
from typing import List

from src.app.buttons.view_issue_button import ViewIssueButton
from src.app.file_manager.common_file_manager import CommonFileManager
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
    def __init__(self, rootManager: RootManager):
        self.RootManager = rootManager
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
        # self.refresh() should populate issues instead
        with open("C:/Users/green/PycharmProjects/DesktopApp/src/app/widget/issues/example_issue_log.json") as issueLog:
            issuesJson = json.load(issueLog)
            self.issues = [self.issueFromJson(issue) for issue in issuesJson["issueLog"]]
        self.generateEntries()

    def generateEntries(self):
        row = 0
        headerLabel = tk.Label(
            self.issueLogFrame,
            text=f'All Issues ({len(self.issues)}):',
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


        for issue in self.issues:
            button = ViewIssueButton(
                self.issueLogFrame,
                self.viewIssue,
                issue,
            ).viewIssueButton
            button.grid(row=row, column=0, pady=15)
            row += 1

    def viewIssue(self, issue: Issue):
        ViewIssuePopup(self.RootManager, issue, self.updateIssue)

    def createIssue(self):
        self.syncFromS3()
        # some popup that creates an issue
        self.syncToS3()

    def updateIssue(self, issue: Issue):
        self.syncFromS3()
        self.issues = self.findAndReplace(self.issues, issue)
        self.syncToS3()

    def syncFromS3(self):
        # Get file from S3 and update issues
        pass

    def syncToS3(self):
        # Convert to json and send file to S3
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
