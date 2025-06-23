#!/usr/bin/env python3
import re
import json
import sys
import os


def get_password_requirements():
    """Read the current password requirements from /etc/security/faillock.conf and /etc/security/pwquality.conf."""
    requirements = {
        'LOCKOUT_MINUTES': None,
        'LOCKOUT_RETRIES': None,
        'MINIMUM_PASSWORD_LENGTH': None
    }

    try:
        config_file = '/etc/security/faillock.conf'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()

            # Get unlock_time (in seconds) and convert to minutes
            unlock_time_match = re.search(r'^\s*unlock_time\s*=\s*(\d+)', content, re.MULTILINE)
            if unlock_time_match:
                unlock_time_seconds = int(unlock_time_match.group(1))
                requirements['LOCKOUT_MINUTES'] = unlock_time_seconds // 60  # Convert seconds to minutes
            else:
                # Default value if not specified (600 seconds = 10 minutes)
                requirements['LOCKOUT_MINUTES'] = 10

            # Get deny threshold
            deny_match = re.search(r'^\s*deny\s*=\s*(\d+)', content, re.MULTILINE)
            if deny_match:
                requirements['LOCKOUT_RETRIES'] = int(deny_match.group(1))
            else:
                # Default value if not specified
                requirements['LOCKOUT_RETRIES'] = 3
        else:
            # File doesn't exist, use default values
            requirements['LOCKOUT_MINUTES'] = 10
            requirements['LOCKOUT_RETRIES'] = 3

    except Exception as e:
        sys.stderr.write(f"Error reading password requirements from /etc/security/faillock.conf: {e}\n")
        # Return default values on error
        requirements['LOCKOUT_MINUTES'] = 10
        requirements['LOCKOUT_RETRIES'] = 3

    # Get minimum password length from /etc/security/pwquality.conf
    try:
        pwquality_file = '/etc/security/pwquality.conf'
        if os.path.exists(pwquality_file):
            with open(pwquality_file, 'r') as f:
                content = f.read()

            # Get minlen setting
            minlen_match = re.search(r'^\s*minlen\s*=\s*(\d+)', content, re.MULTILINE)
            if minlen_match:
                requirements['MINIMUM_PASSWORD_LENGTH'] = int(minlen_match.group(1))
            else:
                # Default value if not specified
                requirements['MINIMUM_PASSWORD_LENGTH'] = 8
        else:
            # File doesn't exist, use default value
            requirements['MINIMUM_PASSWORD_LENGTH'] = 8

    except Exception as e:
        sys.stderr.write(f"Error reading minimum password length from /etc/security/pwquality.conf: {e}\n")
        # Return default value on error
        requirements['MINIMUM_PASSWORD_LENGTH'] = 8

    return requirements


if __name__ == "__main__":
    # Get current requirements
    current_requirements = get_password_requirements()

    # Output as JSON
    print(json.dumps(current_requirements, indent=2))