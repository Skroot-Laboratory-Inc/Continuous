#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys


def update_password_requirements(requirements_data):
    """
    Update the password requirements in /etc/security/faillock.conf and /etc/security/pwquality.conf.
    Returns True if successful, False otherwise.
    """
    # Extract requirement values
    lockout_minutes = requirements_data.get('LOCKOUT_MINUTES')
    lockout_retries = requirements_data.get('LOCKOUT_RETRIES')
    minimum_password_length = requirements_data.get('MINIMUM_PASSWORD_LENGTH')

    # Check if any values were provided
    if lockout_minutes is None and lockout_retries is None and minimum_password_length is None:
        sys.stderr.write("No requirement values provided. Nothing to update.\n")
        return False

    # Check if running as root
    if os.geteuid() != 0:
        sys.stderr.write("This script requires root privileges. Try running with sudo.\n")
        return False

    # Track overall success
    success = True

    # Update /etc/security/faillock.conf if we have lockout settings
    if lockout_minutes is not None or lockout_retries is not None:
        faillock_success = update_faillock_conf(lockout_minutes, lockout_retries)
        success = success and faillock_success

    # Update /etc/security/pwquality.conf if we have password length setting
    if minimum_password_length is not None:
        pwquality_success = update_pwquality_conf(minimum_password_length)
        success = success and pwquality_success

    return success


def update_faillock_conf(lockout_minutes, lockout_retries):
    """
    Update the password requirements in /etc/security/faillock.conf.
    Returns True if successful, False otherwise.
    """
    config_file = '/etc/security/faillock.conf'
    try:
        # Check if file exists, create if it doesn't
        if not os.path.exists(config_file):
            default_content = [
                "dir = /var/run/faillock\n",
                "audit\n",
                f"deny = {lockout_retries if lockout_retries is not None else 3}\n",
                "fail_interval = 900\n",
                f"unlock_time = {lockout_minutes * 60 if lockout_minutes is not None else 600}\n",
            ]
            with open(config_file, 'w') as f:
                f.writelines(default_content)
            print(f"Created {config_file} with lockout settings")
            return True

        # Read the current file
        with open(config_file, 'r') as f:
            lines = f.readlines()

        # Create a backup
        with open(f'{config_file}.bak', 'w') as f:
            f.writelines(lines)

        # Track which settings we've found and updated
        deny_exists = False
        unlock_time_exists = False
        new_lines = []

        for line in lines:
            stripped_line = line.strip()

            # Handle deny setting
            if stripped_line.startswith('deny =') or stripped_line.startswith('deny='):
                if lockout_retries is not None:
                    new_lines.append(f"deny = {lockout_retries}\n")
                    deny_exists = True
                else:
                    new_lines.append(line)
            # Handle unlock_time setting
            elif stripped_line.startswith('unlock_time =') or stripped_line.startswith('unlock_time='):
                if lockout_minutes is not None:
                    # Convert minutes to seconds
                    unlock_time_seconds = lockout_minutes * 60
                    new_lines.append(f"unlock_time = {unlock_time_seconds}\n")
                    unlock_time_exists = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Add settings if they don't exist
        if lockout_retries is not None and not deny_exists:
            new_lines.append(f"deny = {lockout_retries}\n")

        if lockout_minutes is not None and not unlock_time_exists:
            unlock_time_seconds = lockout_minutes * 60
            new_lines.append(f"unlock_time = {unlock_time_seconds}\n")

        # Write the updated file
        with open(config_file, 'w') as f:
            f.writelines(new_lines)

        success_messages = []
        if lockout_retries is not None:
            success_messages.append(f"deny = {lockout_retries}")
        if lockout_minutes is not None:
            success_messages.append(f"unlock_time = {lockout_minutes * 60} ({lockout_minutes} minutes)")

        print(f"Successfully updated {config_file} with: {', '.join(success_messages)}")
        return True

    except Exception as e:
        sys.stderr.write(f"Error updating password requirements: {e}\n")
        # Try to restore from backup if something went wrong
        try:
            subprocess.run(['cp', f'{config_file}.bak', config_file])
            sys.stderr.write(f"Restored {config_file} from backup after error.\n")
        except:
            sys.stderr.write(f"Failed to restore from backup. Please check {config_file}.bak\n")

        return False


def update_pwquality_conf(minimum_password_length):
    """
    Update the minimum password length in /etc/security/pwquality.conf.
    Returns True if successful, False otherwise.
    """
    config_file = '/etc/security/pwquality.conf'
    try:
        # Check if file exists, create if it doesn't
        if not os.path.exists(config_file):
            # Create the file with default content
            default_content = [
                f"minlen = {minimum_password_length}\n",
                "dcredit = -1\n",
                "ucredit = -1\n",
                "lcredit = -1\n",
                "ocredit = -1\n",
                "enforce_for_root\n",
            ]
            with open(config_file, 'w') as f:
                f.writelines(default_content)
            return True

        # Read the current file
        with open(config_file, 'r') as f:
            lines = f.readlines()

        # Create a backup
        with open(f'{config_file}.bak', 'w') as f:
            f.writelines(lines)

        # Track if we found and updated the setting
        minlen_exists = False
        new_lines = []

        for line in lines:
            stripped_line = line.strip()

            # Handle minlen setting
            if stripped_line.startswith('minlen =') or stripped_line.startswith('minlen='):
                new_lines.append(f"minlen = {minimum_password_length}\n")
                minlen_exists = True
            else:
                new_lines.append(line)

        # Add setting if it doesn't exist
        if not minlen_exists:
            new_lines.append(f"minlen = {minimum_password_length}\n")

        # Write the updated file
        with open(config_file, 'w') as f:
            f.writelines(new_lines)

        print(f"Successfully updated {config_file} with minlen = {minimum_password_length}")
        return True

    except Exception as e:
        sys.stderr.write(f"Error updating minimum password length: {e}\n")
        # Try to restore from backup if something went wrong
        try:
            subprocess.run(['cp', f'{config_file}.bak', config_file])
            sys.stderr.write(f"Restored {config_file} from backup after error.\n")
        except:
            sys.stderr.write(f"Failed to restore from backup. Please check {config_file}.bak\n")

        return False


def parse_arguments():
    parser = argparse.ArgumentParser(description='Update password requirements in faillock.conf')
    parser.add_argument('--file', '-f', type=str, help='JSON file containing requirement settings')
    parser.add_argument('--json', '-j', type=str, help='JSON string containing requirement settings')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # Load requirements data
    requirements_data = None

    if args.file:
        try:
            with open(args.file, 'r') as f:
                requirements_data = json.load(f)
        except Exception as e:
            sys.stderr.write(f"Error reading JSON file: {e}\n")
            sys.exit(1)
    elif args.json:
        try:
            requirements_data = json.loads(args.json)
        except Exception as e:
            sys.stderr.write(f"Error parsing JSON string: {e}\n")
            sys.exit(1)
    else:
        sys.stderr.write("Error: Either --file or --json argument is required\n")
        sys.exit(1)

    # Update requirements in /etc/security/faillock.conf
    if not update_password_requirements(requirements_data):
        sys.exit(1)
