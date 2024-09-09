import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Callable

from src.app.helper.helper_functions import makeToplevelScrollable, formatDateTime, datetimeToMillis, millisToDatetime
from src.app.model.issue.issue import Issue
from src.app.model.issue.timestamped_message import TimestampedMessage
from src.app.theme.font_theme import FontTheme
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.popup_interface import PopupInterface


class ViewIssuePopup(PopupInterface):
    def __init__(self, rootManager: RootManager, issue: Issue, updateIssueFn: Callable[[Issue], None]):
        windowRoot = rootManager.createTopLevel()
        self.issue = issue
        self.fonts = FontTheme()
        self.updateIssue = updateIssueFn
        windowRoot, self.window = makeToplevelScrollable(windowRoot, self.fillOutWindowFn)

    def fillOutWindowFn(self, window: tk.Frame):
        for widget in window.winfo_children():
            widget.destroy()
        window.grid_columnconfigure(0, minsize=50)
        window.grid_columnconfigure(1, minsize=350)
        window.grid_columnconfigure(2, minsize=50)
        window.grid_configure(sticky='NESW')
        row = 0
        issueId = tk.Label(
            window,
            text=f'Issue {self.issue.issueId}: {self.issue.title}',
            bg='white',
            font=self.fonts.header1)
        issueId.grid(row=row, column=0, columnspan=3, sticky='nw')
        row += 1
        row = self.createSeparatorLine(window, row)

        for message in self.issue.messages:
            timestampLabel = tk.Label(
                window,
                text=formatDateTime(millisToDatetime(message.timestamp)),
                bg='white',
                font=self.fonts.italicUnderline)
            timestampLabel.grid(row=row, columnspan=3, column=0, sticky='nw')
            row += 1
            messageLabel = tk.Label(
                window,
                text=message.entry,
                bg='white',
                font=self.fonts.primary,
                wraplength=750)
            messageLabel.grid(row=row, columnspan=3, column=0, sticky='nw', pady=(0, 15))
            row += 1

        if not self.issue.resolved:
            self.messageEntry = tk.Entry(window, bg='white', font=self.fonts.primary)
            self.messageEntry.grid(row=row, columnspan=3, column=0, sticky='nesw', pady=(0, 15))
            row += 1

            resolveIssue = ttk.Button(
                window,
                text="Resolve Issue",
                style='W.TButton',
                command=lambda: self.resolve(),
            )
            resolveIssue.grid(row=row, column=0, sticky='nw')

            submitMessage = ttk.Button(
                window,
                text="Submit",
                style='W.TButton',
                command=lambda: self.submit(),
            )
            submitMessage.grid(row=row, column=2, sticky='ne')

    def resolve(self):
        self.issue.resolveIssue()
        self.updateIssue(self.issue)
        self.fillOutWindowFn(self.window)

    def submit(self):
        issueMessage = TimestampedMessage(datetimeToMillis(datetime.now()), self.messageEntry.get())
        self.messageEntry.delete(0, 'end')
        self.issue.messages.append(issueMessage)
        self.updateIssue(self.issue)
        self.fillOutWindowFn(self.window)

    @staticmethod
    def createSeparatorLine(window, row):
        ttk.Separator(window, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky='ew', pady=(0, 15))
        row += 1
        return row
