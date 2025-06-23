import time

from src.app.authentication.helpers.functions import getRole


class SessionUser:
    def __init__(self, username: str):
        self.username = username
        self.loginTime = time.time()
        self.userRole = getRole(username)

