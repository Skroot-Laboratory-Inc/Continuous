#!/usr/bin/env python3

from src.app.common_modules.authentication.helpers.exceptions import InvalidConfiguration
from src.app.common_modules.authentication.password_policy_manager.password_policy_manager import PasswordPolicyManager


class DevPasswordPolicyManager(PasswordPolicyManager):
    """
    A class to manage Ubuntu password policies programmatically given that the user has permissions.

    Attributes:
        max_days (int): Maximum password age in days
        min_days (int): Minimum password age in days
        warn_age (int): Number of days to warn before password expiration
        inactive_days (int): Number of days after password expiration until account is locked
    """

    def __init__(self):
        """
        Initialize the password policy manager with the paths to the scripts.
        Automatically fetches current policy settings when instantiated.

        Raises:
            RuntimeError: If unable to get current policy settings
        """
        self.max_days = 90
        self.min_days = 1
        self.warn_age = 7
        self.inactive_days = 30

    def update_policy(self, apply_to_users=True, max_days=None, min_days=None, warn_age=None, inactive_days=None):
        """
        Update the password policy using provided parameters or current class attributes.

        Args:
            apply_to_users (bool): Whether to apply the policy to existing system users
            max_days (int, optional): Maximum password age in days
            min_days (int, optional): Minimum password age in days
            warn_age (int, optional): Number of days to warn before password expiration
            inactive_days (int, optional): Number of days after expiration until account lockout

        Returns:
            bool: True if successful, False otherwise
        """
        # Build policy dictionary using provided parameters or current attributes
        is_valid, error_message = self.validate_policy_values(max_days, min_days, warn_age, inactive_days)
        if not is_valid:
            raise InvalidConfiguration(error_message)
        policy_dict = {}

        if max_days is not None:
            policy_dict['PASS_MAX_DAYS'] = max_days
            self.max_days = max_days
        elif self.max_days is not None:
            policy_dict['PASS_MAX_DAYS'] = self.max_days

        if min_days is not None:
            policy_dict['PASS_MIN_DAYS'] = min_days
            self.min_days = min_days
        elif self.min_days is not None:
            policy_dict['PASS_MIN_DAYS'] = self.min_days

        if warn_age is not None:
            policy_dict['PASS_WARN_AGE'] = warn_age
            self.warn_age = warn_age
        elif self.warn_age is not None:
            policy_dict['PASS_WARN_AGE'] = self.warn_age

        if inactive_days is not None:
            policy_dict['INACTIVE_DAYS'] = inactive_days
            self.inactive_days = inactive_days
        elif self.inactive_days is not None:
            policy_dict['INACTIVE_DAYS'] = self.inactive_days

        # If no values provided and no attributes set, return error
        if not policy_dict:
            raise InvalidConfiguration("No policy values provided for update")

