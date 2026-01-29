"""
Device Credentials Manager

Manages AWS temporary credentials using device ID and device secret.
- Reads device credentials from platform-specific locations
- Fetches temporary credentials from API Gateway
- Caches credentials in memory and sets environment variables
- Proactively refreshes when credentials have <= 5 minutes remaining
- Retries on failure (1-2 times) with exponential backoff
- Only logs failures when internet connectivity is present
"""

import json
import logging
import os
import platform
import threading
import time
from datetime import datetime, timezone
from typing import Optional, Tuple

import requests

from src.app.common_modules.wifi.helpers.wifi_helpers import checkInternetConnection

# API Gateway endpoint for credential vending
CREDENTIALS_API_URL = "https://uf0au6nv6e.execute-api.us-east-2.amazonaws.com/v1/credentials"

# Credential refresh buffer (refresh when <= 5 minutes remaining)
REFRESH_BUFFER_SECONDS = 300

# Retry configuration
MAX_RETRIES = 2
RETRY_DELAYS = [2, 4]  # seconds between retries


class DeviceCredentialsManager:
    """
    Singleton manager for device-based AWS credentials.

    Handles:
    - Loading device ID and secret from platform-specific locations
    - Fetching temporary credentials from API Gateway
    - Caching and auto-refreshing credentials
    - Setting AWS environment variables
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._device_id: Optional[str] = None
        self._device_secret: Optional[str] = None
        self._access_key_id: Optional[str] = None
        self._secret_access_key: Optional[str] = None
        self._session_token: Optional[str] = None
        self._expiration: Optional[datetime] = None
        self._credentials_lock = threading.Lock()
        self._last_fetch_failed = False
        self._validation_state: Optional[bool] = None  # Cached validation result
        self._validation_lock = threading.Lock()
        self._background_fetch_in_progress = False
        self._caller_arn: Optional[str] = None  # Cached STS caller ARN

    def _get_device_config_path(self) -> str:
        """
        Get the platform-specific path to the device configuration file.

        Returns:
            str: Path to device.json
            - Linux: /etc/skroot/device.json
            - Windows: %PROGRAMDATA%\\Skroot\\device.json
        """
        if platform.system() == "Windows":
            program_data = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
            return os.path.join(program_data, "Skroot", "device.json")
        else:
            return "/etc/skroot/device.json"

    def _load_device_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Load device ID and secret from the configuration file.

        Returns:
            Tuple of (device_id, device_secret) or (None, None) if not found/invalid
        """
        config_path = self._get_device_config_path()

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            device_id = config.get('device_id')
            device_secret = config.get('device_secret')

            if not device_id or not device_secret:
                logging.warning(
                    f"Device config at {config_path} missing device_id or device_secret",
                    extra={"id": "AWS"}
                )
                return None, None

            return device_id, device_secret

        except FileNotFoundError:
            logging.warning(
                f"Device config not found at {config_path}",
                extra={"id": "AWS"}
            )
            return None, None
        except json.JSONDecodeError as e:
            logging.error(
                f"Invalid JSON in device config at {config_path}: {e}",
                extra={"id": "AWS"}
            )
            return None, None
        except Exception as e:
            logging.error(
                f"Error reading device config at {config_path}: {e}",
                extra={"id": "AWS"}
            )
            return None, None

    def _fetch_credentials(self, device_id: str, device_secret: str) -> bool:
        """
        Fetch temporary credentials from the API Gateway.

        Args:
            device_id: The device identifier
            device_secret: The device secret

        Returns:
            bool: True if credentials were successfully fetched, False otherwise
        """
        payload = {
            "device_id": device_id,
            "device_secret": device_secret
        }

        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = requests.post(
                    CREDENTIALS_API_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()

                    with self._credentials_lock:
                        self._access_key_id = data.get('accessKeyId')
                        self._secret_access_key = data.get('secretAccessKey')
                        self._session_token = data.get('sessionToken')

                        # Parse expiration time
                        expiration_str = data.get('expiration')
                        if expiration_str:
                            # Handle ISO format: "2026-01-29T17:06:21.000Z"
                            self._expiration = datetime.fromisoformat(
                                expiration_str.replace('Z', '+00:00')
                            )

                        # Set environment variables for boto3
                        self._set_environment_variables()

                    self._last_fetch_failed = False
                    logging.info(
                        f"Successfully fetched AWS credentials for device {device_id}, "
                        f"expires at {self._expiration}",
                        extra={"id": "AWS"}
                    )
                    return True

                else:
                    last_error = f"API returned status {response.status_code}: {response.text}"

            except requests.exceptions.Timeout:
                last_error = "Request timed out"
            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
            except requests.exceptions.RequestException as e:
                last_error = f"Request failed: {e}"
            except Exception as e:
                last_error = f"Unexpected error: {e}"

            # Retry with delay if not the last attempt
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAYS[attempt])

        # All retries failed - only log if internet is available
        self._last_fetch_failed = True
        if checkInternetConnection(timeout=2):
            logging.error(
                f"Failed to fetch AWS credentials after {MAX_RETRIES + 1} attempts: {last_error}",
                extra={"id": "AWS"}
            )

        return False

    def _set_environment_variables(self):
        """
        Set AWS credential environment variables for boto3.
        Must be called with _credentials_lock held.
        """
        if self._access_key_id:
            os.environ['AWS_ACCESS_KEY_ID'] = self._access_key_id
        if self._secret_access_key:
            os.environ['AWS_SECRET_ACCESS_KEY'] = self._secret_access_key
        if self._session_token:
            os.environ['AWS_SESSION_TOKEN'] = self._session_token

    def _clear_environment_variables(self):
        """Clear AWS credential environment variables."""
        for var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
            os.environ.pop(var, None)

    def _credentials_need_refresh(self) -> bool:
        """
        Check if credentials need to be refreshed.

        Returns:
            bool: True if credentials are missing, expired, or expiring soon
        """
        with self._credentials_lock:
            if not self._access_key_id or not self._secret_access_key:
                return True

            if not self._expiration:
                return True

            # Check if credentials expire within the buffer period
            now = datetime.now(timezone.utc)
            time_remaining = (self._expiration - now).total_seconds()

            return time_remaining <= REFRESH_BUFFER_SECONDS

    def ensure_valid_credentials(self) -> bool:
        """
        Ensure valid AWS credentials are available.

        This method:
        1. Loads device credentials if not already loaded
        2. Fetches new temporary credentials if needed
        3. Sets environment variables for boto3

        Returns:
            bool: True if valid credentials are available, False otherwise
        """
        # Load device credentials if not already loaded
        if not self._device_id or not self._device_secret:
            self._device_id, self._device_secret = self._load_device_credentials()

        if not self._device_id or not self._device_secret:
            return False

        # Check if credentials need refresh
        if self._credentials_need_refresh():
            return self._fetch_credentials(self._device_id, self._device_secret)

        return True

    def refresh_credentials(self) -> bool:
        """
        Force a credential refresh.

        Returns:
            bool: True if credentials were successfully refreshed
        """
        if not self._device_id or not self._device_secret:
            self._device_id, self._device_secret = self._load_device_credentials()

        if not self._device_id or not self._device_secret:
            return False

        return self._fetch_credentials(self._device_id, self._device_secret)

    def has_device_config(self) -> bool:
        """
        Check if device configuration file exists and is valid.

        Returns:
            bool: True if device config exists with valid credentials
        """
        device_id, device_secret = self._load_device_credentials()
        return device_id is not None and device_secret is not None

    def get_device_id(self) -> Optional[str]:
        """
        Get the device ID.

        Returns:
            str or None: The device ID if available
        """
        if not self._device_id:
            self._device_id, self._device_secret = self._load_device_credentials()
        return self._device_id

    def get_credentials_expiration(self) -> Optional[datetime]:
        """
        Get the expiration time of current credentials.

        Returns:
            datetime or None: Expiration time if credentials are loaded
        """
        with self._credentials_lock:
            return self._expiration

    def is_credential_fetch_failing(self) -> bool:
        """
        Check if the last credential fetch attempt failed.

        Returns:
            bool: True if the last fetch failed
        """
        return self._last_fetch_failed

    def get_cached_validation_state(self) -> Optional[bool]:
        """
        Get the cached validation state without triggering a new validation.

        Returns:
            bool or None: True if validated, False if validation failed, None if not yet validated
        """
        with self._validation_lock:
            return self._validation_state

    def set_validation_state(self, state: bool, caller_arn: Optional[str] = None):
        """
        Set the cached validation state.

        Args:
            state: True if credentials are valid
            caller_arn: The ARN from STS get-caller-identity (optional)
        """
        with self._validation_lock:
            self._validation_state = state
            if caller_arn:
                self._caller_arn = caller_arn

    def get_caller_arn(self) -> Optional[str]:
        """
        Get the cached STS caller ARN.

        Returns:
            str or None: The ARN if available
        """
        with self._validation_lock:
            return self._caller_arn

    def ensure_valid_credentials_async(self, callback=None):
        """
        Ensure valid AWS credentials in a background thread.

        This method returns immediately and fetches credentials in the background.
        The callback is called with the result (True/False) when complete.

        Args:
            callback: Optional callable that receives the result (bool)
        """
        def _fetch_in_background():
            try:
                result = self.ensure_valid_credentials()
                if callback:
                    callback(result)
            finally:
                self._background_fetch_in_progress = False

        with self._credentials_lock:
            if self._background_fetch_in_progress:
                return  # Already fetching
            self._background_fetch_in_progress = True

        thread = threading.Thread(target=_fetch_in_background, daemon=True)
        thread.start()

    def has_valid_cached_credentials(self) -> bool:
        """
        Check if we have valid cached credentials without making any network calls.

        Returns:
            bool: True if cached credentials exist and are not expired
        """
        with self._credentials_lock:
            if not self._access_key_id or not self._secret_access_key:
                return False

            if not self._expiration:
                return False

            now = datetime.now(timezone.utc)
            return self._expiration > now


# Module-level convenience functions
_manager: Optional[DeviceCredentialsManager] = None


def get_credentials_manager() -> DeviceCredentialsManager:
    """Get the singleton DeviceCredentialsManager instance."""
    global _manager
    if _manager is None:
        _manager = DeviceCredentialsManager()
    return _manager


def ensure_aws_credentials() -> bool:
    """
    Ensure valid AWS credentials are available.

    Convenience function that gets the singleton manager and ensures credentials.

    Returns:
        bool: True if valid credentials are available
    """
    return get_credentials_manager().ensure_valid_credentials()


def refresh_aws_credentials() -> bool:
    """
    Force a refresh of AWS credentials.

    Returns:
        bool: True if credentials were successfully refreshed
    """
    return get_credentials_manager().refresh_credentials()
