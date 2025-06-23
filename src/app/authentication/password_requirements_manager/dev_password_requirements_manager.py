#!/usr/bin/env python3

from src.app.authentication.helpers.exceptions import InvalidConfiguration
from src.app.authentication.password_requirements_manager.password_requirements_manager import PasswordRequirementsManager


class DevPasswordRequirementsManager(PasswordRequirementsManager):
    """
    A class to manage Ubuntu password requirements programmatically given that the user has permissions.

    Attributes:
        lockout_minutes (int): Number of minutes to lock account after failed attempts
        lockout_retries (int): Number of failed attempts before lockout
        minimum_password_length (int): Minimum required password length
    """

    def __init__(self):
        """
        Initialize the password requirements manager.
        Automatically sets default requirement settings when instantiated.

        Raises:
            RuntimeError: If unable to get current requirement settings
        """
        self.lockout_minutes = 10
        self.lockout_retries = 3
        self.minimum_password_length = 8

    def update_requirements(self, lockout_minutes=None, lockout_retries=None, minimum_password_length=None):
        """
        Update the password requirements using provided parameters or current class attributes.

        Args:
            lockout_minutes (int, optional): Number of minutes to lock account after failed attempts
            lockout_retries (int, optional): Number of failed attempts before lockout
            minimum_password_length (int, optional): Minimum required password length

        Returns:
            bool: True if successful, False otherwise
        """
        # Build requirements dictionary using provided parameters or current attributes
        is_valid, error_message = self.validate_requirement_values(lockout_minutes, lockout_retries, minimum_password_length)
        if not is_valid:
            raise InvalidConfiguration(error_message)
        requirements_dict = {}

        if lockout_minutes is not None:
            requirements_dict['LOCKOUT_MINUTES'] = lockout_minutes
            self.lockout_minutes = lockout_minutes
        elif self.lockout_minutes is not None:
            requirements_dict['LOCKOUT_MINUTES'] = self.lockout_minutes

        if lockout_retries is not None:
            requirements_dict['LOCKOUT_RETRIES'] = lockout_retries
            self.lockout_retries = lockout_retries
        elif self.lockout_retries is not None:
            requirements_dict['LOCKOUT_RETRIES'] = self.lockout_retries

        if minimum_password_length is not None:
            requirements_dict['MINIMUM_PASSWORD_LENGTH'] = minimum_password_length
            self.minimum_password_length = minimum_password_length
        elif self.minimum_password_length is not None:
            requirements_dict['MINIMUM_PASSWORD_LENGTH'] = self.minimum_password_length

        # If no values provided and no attributes set, return error
        if not requirements_dict:
            raise InvalidConfiguration("No requirement values provided for update")
