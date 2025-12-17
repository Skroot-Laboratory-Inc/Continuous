#!/usr/bin/env python3
import json
import subprocess

from src.app.common_modules.authentication.helpers.constants import AuthenticationConstants
from src.app.common_modules.authentication.helpers.exceptions import InvalidConfiguration, ConfigurationException


class PasswordRotationManager:
    """
    A class to manage Ubuntu password policies programmatically given that the user has permissions.

    Attributes:
        max_days (int): Maximum password age in days
        inactive_days (int): Number of days after password expiration until account is locked
        historic_passwords (int): Number of historic passwords to remember
    """

    def __init__(self):
        """
        Initialize the password policy manager with the paths to the scripts.
        Automatically fetches current policy settings when instantiated.

        Raises:
            RuntimeError: If unable to get current policy settings
        """
        # Initialize policy attributes with None
        self.max_days = None
        self.inactive_days = None
        self.historic_passwords = None

        # Get current policy settings
        self.refresh_policy()

    def refresh_policy(self):
        """
        Refresh the current policy settings from the system.
        Updates the class attributes with the current values.
        """
        try:
            policy = self.get_policy()

            # Update attributes with current values
            self.max_days = policy.get('PASS_MAX_DAYS')
            self.inactive_days = policy.get('INACTIVE_DAYS')
            self.historic_passwords = policy.get('HISTORIC_PASSWORDS')
        except Exception as e:
            raise ConfigurationException(e)

    def update_policy(self, apply_to_users=True, max_days=None, inactive_days=None, historic_passwords=None):
        """
        Update the password policy using provided parameters or current class attributes.

        Args:
            apply_to_users (bool): Whether to apply the policy to existing system users
            max_days (int, optional): Maximum password age in days
            inactive_days (int, optional): Number of days after expiration until account lockout
            historic_passwords (int, optional): Number of historic passwords to remember
        """
        # Build policy dictionary using provided parameters or current attributes
        is_valid, error_message = self.validate_policy_values(max_days, inactive_days, historic_passwords)
        if not is_valid:
            raise InvalidConfiguration(error_message)
        policy_dict = {}

        if max_days is not None:
            policy_dict['PASS_MAX_DAYS'] = max_days
        elif self.max_days is not None:
            policy_dict['PASS_MAX_DAYS'] = self.max_days

        if inactive_days is not None:
            policy_dict['INACTIVE_DAYS'] = inactive_days
        elif self.inactive_days is not None:
            policy_dict['INACTIVE_DAYS'] = self.inactive_days

        if historic_passwords is not None:
            policy_dict['HISTORIC_PASSWORDS'] = historic_passwords
        elif self.historic_passwords is not None:
            policy_dict['HISTORIC_PASSWORDS'] = self.historic_passwords

        # If no values provided and no attributes set, return error
        if not policy_dict:
            raise InvalidConfiguration("No policy values provided for update")

        return self._execute_update(policy_dict, apply_to_users)

    def _execute_update(self, policy_dict, apply_to_users=True):
        """
        Internal method to execute the update script with the given policy dictionary.

        Args:
            policy_dict (dict): Dictionary with policy settings to update
            apply_to_users (bool): Whether to apply the policy to existing system users
        """
        # Convert dict to JSON string
        policy_json = json.dumps(policy_dict)

        try:
            cmd = ['sudo', AuthenticationConstants().updatePasswordPolicies, '--json', policy_json]
            if apply_to_users:
                cmd.append('--apply-users')

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise ConfigurationException(result.stderr)

            # Refresh policy settings after successful update
            self.refresh_policy()
        except Exception as e:
            raise ConfigurationException(e)

    def validate_policy_values(self, max_days=None, inactive_days=None, historic_passwords=None):
        """
        Validate password policy values to ensure they're within safe ranges.
        Returns a tuple of (is_valid, error_message)
        """
        if max_days is not None:
            if not isinstance(max_days, int) or max_days < 1:
                return False, "Max Password Age must be a positive integer"
            if max_days > 99999:
                return False, "Max Password Age exceeds maximum value (99999)"

        if inactive_days is not None:
            if not isinstance(inactive_days, int) or (inactive_days < -1):
                return False, "Inactive Days must be -1 or a positive integer"

        if historic_passwords is not None:
            if not isinstance(historic_passwords, int) or historic_passwords < 0:
                return False, "Historic Passwords must be a non-negative integer"
            if historic_passwords > 400:
                return False, "Historic Passwords exceeds maximum recommended value (400)"

        return True, ""

    @staticmethod
    def get_policy():
        """
        Get the current password policy.

        Returns:
            dict: The current policy settings or None if there was an error
        """
        try:
            result = subprocess.run([AuthenticationConstants().getPasswordPolicies],
                                    capture_output=True,
                                    text=True)

            if result.returncode != 0:
                raise ConfigurationException(result.stdout)

            return json.loads(result.stdout)
        except Exception as e:
            raise ConfigurationException(e)
