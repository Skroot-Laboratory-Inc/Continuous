from src.app.model.issue.issue import Issue
from src.app.theme.colors import Colors
from src.app.theme.font_theme import FontTheme
from src.app.widget.link_button import Linkbutton


class ViewIssueButton:
    def __init__(self, master, invokeFn, issue: Issue):
        self.Colors = Colors()
        self.viewIssueButton = Linkbutton(
            master,
            font=FontTheme().header3,
            text=f"Issue {issue.issueId}: {issue.title}",
            command=lambda: invokeFn(issue),
        )

    def destroySelf(self):
        self.viewIssueButton.destroy()

