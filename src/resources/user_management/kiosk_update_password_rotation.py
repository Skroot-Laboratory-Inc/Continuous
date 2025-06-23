#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys


def update_password_policy(policy_data):
    """
    Update the password policy in /etc/login.defs, /etc/default/useradd, and /etc/security/pwhistory.conf.
    Returns True if successful, False otherwise.
    """
    # Extract policy values
    max_days = policy_data.get('PASS_MAX_DAYS')
    inactive_days = policy_data.get('INACTIVE_DAYS')
    historic_passwords = policy_data.get('HISTORIC_PASSWORDS')

    # Check if any values were provided
    if max_days is None and inactive_days is None and historic_passwords is None:
        sys.stderr.write("No policy values provided. Nothing to update.\n")
        return False

    # Check if running as root
    if os.geteuid() != 0:
        sys.stderr.write("This script requires root privileges. Try running with sudo.\n")
        return False

    # Track overall success
    success = True

    # Update /etc/login.defs if we have max_days
    if max_days is not None:
        success = update_login_defs(max_days)

    # Update /etc/default/useradd if we have inactive days
    if inactive_days is not None:
        inactive_success = update_inactive_days(inactive_days)
        success = success and inactive_success

    # Update /etc/security/pwhistory.conf if we have historic passwords
    if historic_passwords is not None:
        historic_success = update_historic_passwords(historic_passwords)
        success = success and historic_success

    return success


def update_login_defs(max_days):
    """
    Update the password policy in /etc/login.defs.
    Returns True if successful, False otherwise.
    """
    try:
        # Read the current file
        with open('/etc/login.defs', 'r') as f:
            lines = f.readlines()

        # Create a backup
        with open('/etc/login.defs.bak', 'w') as f:
            f.writelines(lines)

        # Process each line and modify the target settings
        new_lines = []
        for line in lines:
            if line.strip().startswith('PASS_MAX_DAYS') and max_days is not None:
                new_lines.append(f"PASS_MAX_DAYS {max_days}\n")
            else:
                new_lines.append(line)

        # Write the updated file
        with open('/etc/login.defs', 'w') as f:
            f.writelines(new_lines)

        print("Password policy updated successfully in /etc/login.defs")
        return True

    except Exception as e:
        sys.stderr.write(f"Error updating policy in /etc/login.defs: {e}\n")
        # Try to restore from backup if something went wrong
        try:
            subprocess.run(['cp', '/etc/login.defs.bak', '/etc/login.defs'])
            sys.stderr.write("Restored from backup after error.\n")
        except:
            sys.stderr.write("Failed to restore from backup. Please check /etc/login.defs.bak\n")

        return False


def update_inactive_days(inactive_days):
    """
    Update the INACTIVE setting in /etc/default/useradd.
    Returns True if successful, False otherwise.
    """
    try:
        # First, read the current file
        with open('/etc/default/useradd', 'r') as f:
            lines = f.readlines()

        # Create a backup
        with open('/etc/default/useradd.bak', 'w') as f:
            f.writelines(lines)

        # Check if INACTIVE setting exists
        inactive_exists = False
        new_lines = []

        for line in lines:
            if line.strip().startswith('INACTIVE='):
                # Replace the line
                new_lines.append(f"INACTIVE={inactive_days}\n")
                inactive_exists = True
            else:
                new_lines.append(line)

        # If INACTIVE setting doesn't exist, add it
        if not inactive_exists:
            new_lines.append(f"INACTIVE={inactive_days}\n")

        # Write the updated file
        with open('/etc/default/useradd', 'w') as f:
            f.writelines(new_lines)

        print(f"Successfully updated INACTIVE days to {inactive_days} in /etc/default/useradd")
        return True

    except Exception as e:
        sys.stderr.write(f"Error updating INACTIVE days: {e}\n")
        # Try to restore from backup if something went wrong
        try:
            subprocess.run(['cp', '/etc/default/useradd.bak', '/etc/default/useradd'])
            sys.stderr.write("Restored /etc/default/useradd from backup after error.\n")
        except:
            sys.stderr.write("Failed to restore from backup. Please check /etc/default/useradd.bak\n")

        return False


def update_historic_passwords(historic_passwords):
    """
    Update the remember setting in /etc/security/pwhistory.conf.
    Returns True if successful, False otherwise.
    """
    config_file = '/etc/security/pwhistory.conf'
    try:

        # Check if file exists, create if it doesn't
        if not os.path.exists(config_file):
            default_content = [
                "enforce_for_root\n",
                f"remember = {historic_passwords}\n",
                "file = /etc/security/opasswd\n"
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

        # Check if remember setting exists
        remember_exists = False
        new_lines = []

        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('remember =') or stripped_line.startswith('remember='):
                # Replace the line
                new_lines.append(f"remember = {historic_passwords}\n")
                remember_exists = True
            else:
                new_lines.append(line)

        # If remember setting doesn't exist, add it
        if not remember_exists:
            new_lines.append(f"remember = {historic_passwords}\n")

        # Write the updated file
        with open(config_file, 'w') as f:
            f.writelines(new_lines)

        print(f"Successfully updated remember to {historic_passwords} in {config_file}")
        return True

    except Exception as e:
        sys.stderr.write(f"Error updating historic passwords: {e}\n")
        # Try to restore from backup if something went wrong
        try:
            subprocess.run(['cp', f'{config_file}.bak', config_file])
            sys.stderr.write(f"Restored {config_file} from backup after error.\n")
        except:
            sys.stderr.write(f"Failed to restore from backup. Please check {config_file}.bak\n")

        return False


def apply_to_system_users(policy_data):
    """
    Apply password policy to existing system users.
    Returns the number of users updated.
    """
    # Extract policy values
    max_days = policy_data.get('PASS_MAX_DAYS')
    inactive_days = policy_data.get('INACTIVE_DAYS')

    # Check if running as root
    if os.geteuid() != 0:
        sys.stderr.write("This function requires root privileges. Try running with sudo.\n")
        return 0

    # Prepare the chage command options
    chage_options = []
    if max_days is not None:
        chage_options.append(f"-M {max_days}")
    if inactive_days is not None:
        chage_options.append(f"-I {inactive_days}")

    if not chage_options:
        sys.stderr.write("No policy options specified for user updates.\n")
        return 0

    # UID range for system users
    min_uid = 100
    max_uid = 999

    # Get list of system users in the specified UID range
    try:
        users = []
        with open('/etc/passwd', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 4:
                    username, _, uid, _ = parts[0:4]
                    try:
                        uid = int(uid)
                        if min_uid <= uid <= max_uid:
                            # Skip users with nologin or false shells
                            if not parts[6].endswith(('/sbin/nologin', '/bin/false')):
                                users.append(username)
                    except ValueError:
                        continue

        # Apply changes to each user
        updated_count = 0
        for username in users:
            cmd = ['chage'] + [opt for opt in ' '.join(chage_options).split()] + [username]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Updated policy for system user: {username}")
                updated_count += 1
            else:
                sys.stderr.write(f"Failed to update {username}: {result.stderr}\n")

        print(f"Updated {updated_count} out of {len(users)} system users.")
        return updated_count

    except Exception as e:
        sys.stderr.write(f"Error applying policy to users: {e}\n")
        return 0


def parse_arguments():
    parser = argparse.ArgumentParser(description='Update password policy and apply to system users')
    parser.add_argument('--file', '-f', type=str, help='JSON file containing policy settings')
    parser.add_argument('--json', '-j', type=str, help='JSON string containing policy settings')
    parser.add_argument('--apply-users', '-a', action='store_true',
                        help='Apply policy to existing system users')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # Load policy data
    policy_data = None

    if args.file:
        try:
            with open(args.file, 'r') as f:
                policy_data = json.load(f)
        except Exception as e:
            sys.stderr.write(f"Error reading JSON file: {e}\n")
            sys.exit(1)
    elif args.json:
        try:
            policy_data = json.loads(args.json)
        except Exception as e:
            sys.stderr.write(f"Error parsing JSON string: {e}\n")
            sys.exit(1)
    else:
        sys.stderr.write("Error: Either --file or --json argument is required\n")
        sys.exit(1)

    # Update policy in /etc/login.defs
    if not update_password_policy(policy_data):
        sys.exit(1)

    # Apply to system users if requested
    if args.apply_users:
        apply_to_system_users(policy_data)
