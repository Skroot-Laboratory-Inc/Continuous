from typing import Optional

from src.app.common_modules.authentication.helpers.configuration import AuthConfiguration
from src.app.common_modules.authentication.helpers.functions import validateUserCredentials
from src.app.common_modules.authentication.helpers.logging import logAuthAction
from src.app.common_modules.authentication.helpers.sign_out_timer import SignOutTimer
from src.app.common_modules.authentication.session_manager.session_user import SessionUser
from src.app.widget import text_notification


class SessionManager:
    def __init__(self, timeoutMinutes=15):
        self.timeoutSeconds = timeoutMinutes * 60
        self.user: Optional[SessionUser] = None
        self.activityTimer = SignOutTimer(self.timeoutSeconds, self.expireSession)

    def login(self, username, password):
        validateUserCredentials(username, password)
        self.user = SessionUser(username)
        self.activityTimer.start()
        return True

    def logout(self):
        text_notification.setText(f"{self.user.username} logged out.")
        self.activityTimer.stop()
        self.clearUser()

    def expireSession(self):
        text_notification.setText(f"Session expired for {self.user.username}, please sign in again.")
        self.clearUser()

    def clearUser(self):
        logAuthAction(
            "Logout",
            "Successful",
            self.user.username,
        )
        self.user = None

    def isValidSession(self):
        if self.user is None:
            return False

        if not self.activityTimer.isRunning:
            self.expireSession()
            return False

        self.activityTimer.refresh()
        return True

    def getUser(self) -> str:
        if AuthConfiguration().getConfig():
            return self.user.username
        else:
            return ""
