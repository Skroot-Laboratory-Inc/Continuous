from typing import Protocol

from src.app.common_modules.authentication.authentication_popup import AuthenticationPopup
from src.app.common_modules.authentication.model.user_role import UserRole
from src.app.widget import text_notification


class HasAuthentication(Protocol):
    rootManager: 'RootManager'
    sessionManager: 'SessionManager'


def requireUser(func):
    """Decorator for functions that require any authenticated user"""
    def wrapper(self: HasAuthentication, *args, **kwargs):
        if self.sessionManager.isValidSession():
            return func(self, *args, **kwargs)
        else:
            auth = AuthenticationPopup(self.rootManager, self.sessionManager)
            if auth.isAuthenticated:
                return func(self, *args, **kwargs)
            else:
                return None
    return wrapper


def requireAdmin(func):
    """Decorator for functions that require admin or system admin access"""
    def wrapper(self: HasAuthentication, *args, **kwargs):
        if self.sessionManager.isValidSession() and self.sessionManager.user.userRole >= UserRole.ADMIN:
            return func(self, *args, **kwargs)
        elif self.sessionManager.isValidSession() and self.sessionManager.user.userRole < UserRole.ADMIN:
            text_notification.setText("Administrator Privileges Required")
        elif not self.sessionManager.isValidSession():
            auth = AuthenticationPopup(self.rootManager, self.sessionManager, True)
            if auth.isAuthenticated:
                return func(self, *args, **kwargs)
            else:
                return None
    return wrapper


def requireSystemAdmin(func):
    """Decorator for functions that require system admin access only"""
    def wrapper(self: HasAuthentication, *args, **kwargs):
        if self.sessionManager.isValidSession() and self.sessionManager.user.userRole == UserRole.SYSTEM_ADMIN:
            return func(self, *args, **kwargs)
        elif self.sessionManager.isValidSession() and self.sessionManager.user.userRole != UserRole.SYSTEM_ADMIN:
            text_notification.setText("System Administrator Privileges Required")
        elif not self.sessionManager.isValidSession():
            auth = AuthenticationPopup(self.rootManager, self.sessionManager, False, True)
            if auth.isAuthenticated:
                return func(self, *args, **kwargs)
            else:
                return None
    return wrapper


def forceRequireSystemAdmin(func):
    """Decorator for functions that require system admin access only"""
    def wrapper(self: HasAuthentication, *args, **kwargs):
        if self.sessionManager.isValidSession() and self.sessionManager.user.userRole == UserRole.SYSTEM_ADMIN:
            return func(self, *args, **kwargs)
        elif self.sessionManager.isValidSession() and self.sessionManager.user.userRole != UserRole.SYSTEM_ADMIN:
            text_notification.setText("System Administrator Privileges Required")
        elif not self.sessionManager.isValidSession():
            auth = AuthenticationPopup(self.rootManager, self.sessionManager, False, True, forceAuthenticate=True)
            if auth.isAuthenticated:
                return func(self, *args, **kwargs)
            else:
                return None
    return wrapper
