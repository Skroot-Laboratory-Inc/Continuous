#!/usr/bin/env python3

from src.app.authentication.helpers.exceptions import InvalidConfiguration
from src.app.authentication.password_policy_manager.password_rotation_manager import PasswordRotationManager


class DevPasswordRotationManager(PasswordRotationManager):
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
        self.max_days = 90
        self.inactive_days = 30
        self.historic_passwords = 3

    def update_policy(self, apply_to_users=True, max_days=None, inactive_days=None, historic_passwords=None):
        """
        Update the password policy using provided parameters or current class attributes.

        Args:
            apply_to_users (bool): Whether to apply the policy to existing system users
            max_days (int, optional): Maximum password age in days
            inactive_days (int, optional): Number of days after expiration until account lockout
            historic_passwords (int, optional): Number of historic passwords to remember

        Returns:
            bool: True if successful, False otherwise
        """
        # Build policy dictionary using provided parameters or current attributes
        is_valid, error_message = self.validate_policy_values(max_days, inactive_days, historic_passwords)
        if not is_valid:
            raise InvalidConfiguration(error_message)
        policy_dict = {}

        if max_days is not None:
            policy_dict['PASS_MAX_DAYS'] = max_days
            self.max_days = max_days
        elif self.max_days is not None:
            policy_dict['PASS_MAX_DAYS'] = self.max_days

        if inactive_days is not None:
            policy_dict['INACTIVE_DAYS'] = inactive_days
            self.inactive_days = inactive_days
        elif self.inactive_days is not None:
            policy_dict['INACTIVE_DAYS'] = self.inactive_days

        if historic_passwords is not None:
            policy_dict['HISTORIC_PASSWORDS'] = historic_passwords
            self.historic_passwords = historic_passwords
        elif self.historic_passwords is not None:
            policy_dict['HISTORIC_PASSWORDS'] = self.historic_passwords

        # If no values provided and no attributes set, return error
        if not policy_dict:
            raise InvalidConfiguration("No policy values provided for update")
