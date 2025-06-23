#!/usr/bin/env python3
import datetime
import json
import re
import subprocess
import sys
import syslog

import pam


def authenticate_user(username, password):
    """Authenticate a user via PAM and log the attempt via syslog."""
    logAuthAction("Authentication Attempt", "Initiated", username)

    p = pam.pam()
    authResult = p.authenticate(username, password)
    authReason = p.reason
    authCode = p.code
    if authCode == 6:
        isLockedOut, duration = get_unlock_time(user)
        if isLockedOut:
            authReason = f"User has been locked out for {int(get_unlock_time_from_config()/60)} minutes."
    if authCode == 7:
        isLockedOut, duration = get_unlock_time(user)
        if isLockedOut:
            authReason = f"`{username}` is locked out for {duration}"
        elif isInactive(username):
            authReason = "Password is locked, contact an administrator for a reset."
    elif authCode == 12:
        if isExpired(username):
            authReason = f"{username}'s password is expired, please reset."
            authResult = True
    if authResult:
        logAuthAction(
            "Authentication Attempt",
            "Successful",
            username
        )
    else:
        logAuthAction("Authentication Attempt", "Failed", username, extra=f"Code {authCode} for reason {authReason}")
    return authResult, authReason, authCode


def logAuthAction(category, action, username, extra=None, result=None) -> bool:
    try:
        """Log user authentication actions in JSON format for Ubuntu kiosk_auth.log"""
        syslog.openlog("kiosk_users", 0, syslog.LOG_LOCAL0)

        # Create log data structure
        log_data = {
            "Category": category,
            "Action": action,
            "Username": username,
            "Timestamp": datetime.datetime.now().isoformat(timespec='seconds')
        }

        if extra:
            log_data["Extra"] = extra
        if result:
            log_data["Result"] = result

        # Convert to JSON string and log
        log_message = json.dumps(log_data, separators=(',', ':'))
        syslog.syslog(syslog.LOG_INFO, log_message)
        return True
    except:
        return False
    finally:
        syslog.closelog()


def getFaillockData(username):
    """
    Parse faillock data for a specific user

    Args:
        username (str): Username to check

    Returns:
        dict: Information about failures including count and latest timestamp
    """
    valid_count = 0
    latest_failure = None

    try:
        cmd_output = subprocess.run(['faillock', '--user', username],
                                    capture_output=True, text=True, check=False)

        if cmd_output.returncode != 0 or not cmd_output.stdout.strip():
            return valid_count, latest_failure

        for line in cmd_output.stdout.splitlines():
            # Skip header or empty lines
            if username in line or not line.strip():
                continue

            # Parse a data line
            parts = line.split()
            if len(parts) >= 5 and parts[-1] == 'V':  # Valid failure
                try:
                    timestamp = datetime.datetime.strptime(
                        f"{parts[0]} {parts[1]}",
                        "%Y-%m-%d %H:%M:%S"
                    )

                    valid_count += 1

                    # Track the latest failure
                    if latest_failure is None or timestamp > latest_failure:
                        latest_failure = timestamp
                except ValueError:
                    # Skip if datetime parsing fails
                    pass
    except Exception as e:
        # Assume the user is not locked out.
        pass
    return valid_count, latest_failure


def isExpired(username):
    return checkUserAttributes(username, "Password expires")


def isInactive(username):
    return checkUserAttributes(username, "Password inactive")


def checkUserAttributes(username, attribute) -> (bool, bool):
    """
    Parse user password information to determine if it is expired or inactive

    Args:
        username (str): Username to check

    Returns:
        bool: Whether the account is inactive
        bool: Whether the account is expired
    """
    boolValue = False
    chage_result = subprocess.run(['sudo', 'chage', '-l', username],
                                  capture_output=True,
                                  text=True,
                                  check=True).stdout.strip()

    for line in chage_result.split('\n'):
        if attribute in line:
            expiry_info = line.split(':', 1)[1].strip()

            if expiry_info.lower() == "never":
                boolValue = False
            else:
                try:
                    # Try to parse the expiry date
                    expiry_date = datetime.datetime.strptime(expiry_info, "%b %d, %Y")
                    today = datetime.datetime.now()

                    if expiry_date < today:
                        boolValue = True
                except:
                    pass
            break
    return boolValue


def get_unlock_time(username) -> (bool, str):
    """
    Calculate when a locked user will be automatically unlocked

    Args:
        username (str): Username to check

    Returns:
        bool, str: is_locked, time_remaining
    """
    unlock_time_seconds = get_unlock_time_from_config()
    errors, lastErrorTime = getFaillockData(username)
    is_locked = errors >= get_deny_threshold()

    if not is_locked or lastErrorTime is None:
        return False, format_time_remaining(0)
    unlock_datetime = lastErrorTime + datetime.timedelta(seconds=unlock_time_seconds)
    seconds_remaining = max(0, (unlock_datetime - datetime.datetime.now()).total_seconds())

    # If seconds_remaining is 0, the user is already unlocked
    if seconds_remaining <= 0:
        return False, format_time_remaining(0)

    return True, format_time_remaining(seconds_remaining)


def get_unlock_time_from_config():
    """Get the unlock_time value from faillock.conf"""
    try:
        with open('/etc/security/faillock.conf', 'r') as f:
            content = f.read()

        # Look for unlock_time=X in the config file
        match = re.search(r'^\s*unlock_time\s*=\s*(\d+)', content, re.MULTILINE)
        if match:
            return int(match.group(1))
    except:
        pass

    # Default value (10 minutes) if not specified
    return 600


def get_deny_threshold():
    """Get the deny threshold from faillock.conf"""
    try:
        with open('/etc/security/faillock.conf', 'r') as f:
            content = f.read()

        # Look for deny=X in the config file
        match = re.search(r'^\s*deny\s*=\s*(\d+)', content, re.MULTILINE)
        if match:
            return int(match.group(1))
    except:
        pass

    # Default value if not specified
    return 3


def format_time_remaining(seconds):
    """Format seconds into a human-readable time string"""
    if seconds <= 0:
        return "now"

    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 and hours == 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return ", ".join(parts)


if __name__ == "__main__":
    input_data = sys.stdin.read().strip()

    try:
        auth_data = json.loads(input_data)
        user = auth_data.get('username', '')
        passwd = auth_data.get('password', '')

        if not user or not passwd:
            print(json.dumps({"success": False, "reason": "Missing credentials"}))
            sys.exit(1)

        result, reason, code = authenticate_user(user, passwd)

        print(json.dumps({"success": result, "reason": reason, "code": code}))
        sys.exit(0 if result else 1)
    except Exception as e:
        print(json.dumps({"success": False, "reason": str(e)}))
        sys.exit(1)
