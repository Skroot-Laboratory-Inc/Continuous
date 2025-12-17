#!/usr/bin/env python3
import json
import subprocess

from src.app.common_modules.authentication.helpers.constants import AuthenticationConstants
from src.app.common_modules.authentication.helpers.exceptions import InvalidConfiguration, ConfigurationException


class PasswordRequirementsManager:
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
        Automatically fetches current requirement settings when instantiated.

        Raises:
            RuntimeError: If unable to get current requirement settings
        """
        # Initialize requirement attributes with None
        self.lockout_minutes = None
        self.lockout_retries = None
        self.minimum_password_length = None

        # Get current requirement settings
        self.refresh_requirements()

    def refresh_requirements(self):
        """
        Refresh the current requirement settings from the system.
        Updates the class attributes with the current values.
        """
        try:
            requirements = self.get_requirements()

            # Update attributes with current values
            self.lockout_minutes = requirements.get('LOCKOUT_MINUTES')
            self.lockout_retries = requirements.get('LOCKOUT_RETRIES')
            self.minimum_password_length = requirements.get('MINIMUM_PASSWORD_LENGTH')
        except Exception as e:
            raise ConfigurationException(e)

    def update_requirements(self, lockout_minutes=None, lockout_retries=None, minimum_password_length=None):
        """
        Update the password requirements using provided parameters or current class attributes.

        Args:
            lockout_minutes (int, optional): Number of minutes to lock account after failed attempts
            lockout_retries (int, optional): Number of failed attempts before lockout
            minimum_password_length (int, optional): Minimum required password length
        """
        # Build requirements dictionary using provided parameters or current attributes
        is_valid, error_message = self.validate_requirement_values(lockout_minutes, lockout_retries, minimum_password_length)
        if not is_valid:
            raise InvalidConfiguration(error_message)
        requirements_dict = {}

        if lockout_minutes is not None:
            requirements_dict['LOCKOUT_MINUTES'] = lockout_minutes
        elif self.lockout_minutes is not None:
            requirements_dict['LOCKOUT_MINUTES'] = self.lockout_minutes

        if lockout_retries is not None:
            requirements_dict['LOCKOUT_RETRIES'] = lockout_retries
        elif self.lockout_retries is not None:
            requirements_dict['LOCKOUT_RETRIES'] = self.lockout_retries

        if minimum_password_length is not None:
            requirements_dict['MINIMUM_PASSWORD_LENGTH'] = minimum_password_length
        elif self.minimum_password_length is not None:
            requirements_dict['MINIMUM_PASSWORD_LENGTH'] = self.minimum_password_length

        # If no values provided and no attributes set, return error
        if not requirements_dict:
            raise InvalidConfiguration("No requirement values provided for update")

        return self._execute_update(requirements_dict)

    def _execute_update(self, requirements_dict):
        """
        Internal method to execute the update script with the given requirements dictionary.

        Args:
            requirements_dict (dict): Dictionary with requirement settings to update
        """
        # Convert dict to JSON string
        requirements_json = json.dumps(requirements_dict)

        try:
            cmd = ['sudo', AuthenticationConstants().updatePasswordRequirements, '--json', requirements_json]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise ConfigurationException(result.stderr)

            # Refresh requirement settings after successful update
            self.refresh_requirements()
        except Exception as e:
            raise ConfigurationException(e)

    def validate_requirement_values(self, lockout_minutes=None, lockout_retries=None, minimum_password_length=None):
        """
        Validate password requirement values to ensure they're within safe ranges.
        Returns a tuple of (is_valid, error_message)
        """
        if lockout_minutes is not None:
            if not isinstance(lockout_minutes, int) or lockout_minutes < 0:
                return False, "Lockout Minutes must be a non-negative integer"
            if lockout_minutes > 1440:  # 24 hours
                return False, "Lockout Minutes exceeds maximum recommended value (1440 minutes/24 hours)"

        if lockout_retries is not None:
            if not isinstance(lockout_retries, int) or lockout_retries < 1:
                return False, "Lockout Retries must be a positive integer"
            if lockout_retries > 10:
                return False, "Lockout Retries exceeds maximum recommended value (10)"

        if minimum_password_length is not None:
            if not isinstance(minimum_password_length, int):
                return False, "Minimum Password Length must be an integer"
            if minimum_password_length < 6 or minimum_password_length > 16:
                return False, "Minimum Password Length must be between 6 and 16 characters"

        return True, ""

    @staticmethod
    def get_requirements():
        """
        Get the current password requirements.

        Returns:
            dict: The current requirement settings or None if there was an error
        """
        try:
            result = subprocess.run([AuthenticationConstants().getPasswordRequirements],
                                    capture_output=True,
                                    text=True)

            if result.returncode != 0:
                raise ConfigurationException(result.stdout)

            return json.loads(result.stdout)
        except Exception as e:
            raise ConfigurationException(e)