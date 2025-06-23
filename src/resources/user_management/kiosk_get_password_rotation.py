#!/usr/bin/env python3
import re
import json
import subprocess
import sys
import os


def get_password_policy():
    """Read the current password policy settings from system files."""
    policy = {
        'PASS_MAX_DAYS': None,
        'INACTIVE_DAYS': None,
        'HISTORIC_PASSWORDS': None
    }

    try:
        # Get settings from /etc/login.defs
        with open('/etc/login.defs', 'r') as f:
            content = f.read()

        # Use regex to find PASS_MAX_DAYS
        pattern = re.compile(r'^PASS_MAX_DAYS\s+(\d+)', re.MULTILINE)
        match = pattern.search(content)
        if match:
            policy['PASS_MAX_DAYS'] = int(match.group(1))
    except Exception as e:
        sys.stderr.write(f"Error reading password policy from /etc/login.defs: {e}\n")

    # Get INACTIVE setting from /etc/default/useradd
    try:
        result = subprocess.run(
            ["grep", "^INACTIVE", "/etc/default/useradd"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                parts = output.split("=")
                if len(parts) > 1:
                    try:
                        policy['INACTIVE_DAYS'] = int(parts[1].strip())
                    except ValueError:
                        policy['INACTIVE_DAYS'] = None
    except Exception as e:
        sys.stderr.write(f"Warning: Could not read INACTIVE setting: {e}\n")

    # Get historic passwords setting from /etc/security/pwhistory.conf
    try:
        config_file = '/etc/security/pwhistory.conf'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()

            # Use regex to find remember setting (handles both "remember = X" and "remember=X")
            pattern = re.compile(r'^remember\s*=\s*(\d+)', re.MULTILINE)
            match = pattern.search(content)
            if match:
                policy['HISTORIC_PASSWORDS'] = int(match.group(1))
        else:
            # File doesn't exist, historic passwords is not configured
            policy['HISTORIC_PASSWORDS'] = None
    except Exception as e:
        sys.stderr.write(f"Warning: Could not read historic passwords setting: {e}\n")

    return policy


if __name__ == "__main__":
    # Get current policy
    current_policy = get_password_policy()

    # Output as JSON
    print(json.dumps(current_policy, indent=2))
