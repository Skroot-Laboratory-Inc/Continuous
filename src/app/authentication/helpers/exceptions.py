class AuthenticationException(Exception):
    """ Base class for the authentication related exceptions. """


class IncorrectPasswordException(AuthenticationException):
    """ Exception thrown when the entered password does not match the username provided. """


class PasswordMismatchException(AuthenticationException):
    """ Exception thrown when the entered password does not match the confirmation password. """


class ResetPasswordException(AuthenticationException):
    """ Exception thrown when an error occurs while resetting password. """
    def __init__(self, message):
        self.message = message


class RetireUserException(AuthenticationException):
    """ Exception thrown when an error occurs while retiring a user. """
    def __init__(self, message):
        self.message = message


class ModifyUserRoleException(AuthenticationException):
    """ Exception thrown when an error occurs while modifying a user role. """
    def __init__(self, message):
        self.message = message


class SystemAdminException(AuthenticationException):
    """ Exception thrown when a user tries to modify the system administrator. """
    def __init__(self, message):
        self.message = message


class InsufficientPermissions(AuthenticationException):
    """ Exception thrown when a user tries to reset a password without permissions. """
    def __init__(self, message):
        self.message = message


class RestoreUserException(AuthenticationException):
    """ Exception thrown when an error occurs while retiring a user. """
    def __init__(self, message):
        self.message = message


class UserNotRetiredException(AuthenticationException):
    """ Exception thrown when attempting to restore a retired user. """


class BadPasswordException(AuthenticationException):
    """ Exception thrown when an error occurs while resetting password. """
    def __init__(self, message):
        self.message = message


class PamException(AuthenticationException):
    """ Exception thrown when PAM has an error message to pass along. """
    def __init__(self, message):
        #  The error message that kiosk_auth_check.py returned
        self.message = message


class PasswordExpired(AuthenticationException):
    """ Exception thrown when a user signs into an expired account. """


class NotAdministratorException(AuthenticationException):
    """ Exception thrown when a user tries to sign in as an administrator. """


class NotSystemAdmin(AuthenticationException):
    """ Exception thrown when a user tries to sign in as a system administrator. """


class UserExistsException(AuthenticationException):
    """ Exception thrown when a user already exists in the system during creation. """


class UserDoesntExistException(AuthenticationException):
    """ Exception thrown when a user doesn't exist during deletion. """


class AuthLogsNotFound(AuthenticationException):
    """ Exception thrown when no auth logs are found. """


class AideLogsNotFound(AuthenticationException):
    """ Exception thrown when no aide logs are found. """


class ConfigurationException(Exception):
    """ Exception thrown when an error occurs while setting configurations. """
    def __init__(self, message):
        self.message = message


class InvalidConfiguration(ConfigurationException):
    """ Exception thrown when an admin tries to set an invalid configuration. """


