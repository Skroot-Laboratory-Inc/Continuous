#!/usr/bin/env python3
import re
import json
import subprocess
import sys


def get_password_policy():
    """Read the current password policy settings from /etc/login.defs."""
    policy = {
        'PASS_MAX_DAYS': None,
        'PASS_MIN_DAYS': None,
        'PASS_WARN_AGE': None
    }

    try:
        # Get settings from /etc/login.defs
        with open('/etc/login.defs', 'r') as f:
            content = f.read()

        # Use regex to find the settings
        for key in policy.keys():
            pattern = re.compile(r'^{}\s+(\d+)'.format(key), re.MULTILINE)
            match = pattern.search(content)
            if match:
                policy[key] = int(match.group(1))
    except Exception as e:
        sys.stderr.write(f"Error reading password policy: {e}\n")
        sys.exit(1)

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
                        policy['INACTIVE_DAYS'] = ""
    except Exception as e:
        sys.stderr.write(f"Warning: Could not read INACTIVE setting: {e}\n")

    return policy


if __name__ == "__main__":
    # Get current policy
    current_policy = get_password_policy()

    # Output as JSON
    print(json.dumps(current_policy, indent=2))
