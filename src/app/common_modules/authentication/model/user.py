import json
import logging
import platform
import subprocess
import re
from datetime import datetime

from src.app.common_modules.authentication.helpers.constants import AuthenticationConstants
from src.app.common_modules.authentication.model.user_role import UserRole


class User:
    def __init__(self, username, isAdmin: bool = False):
        self.username = username
        self.role = UserRole.ADMIN if isAdmin else UserRole.USER
        self.first_name = "-"
        self.last_name = "-"
        self.last_changed = "-"
        self.password_expires = "-"
        self.password_inactive = "-"
        self.account_expires = "-"
        self.last_login = "Never"
        if platform.system() == "Linux":
            self._fetch_name_from_comment()
            self._fetch_password_info()
            self._fetch_last_auth_attempt()

    def _fetch_name_from_comment(self):
        """Parse first and last name from the GECOS comment field in /etc/passwd"""
        try:
            result = subprocess.run(
                ['getent', 'passwd', self.username],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                # GECOS is the 5th field (index 4) in the colon-separated passwd entry
                gecos = result.stdout.strip().split(':')[4]
                parts = gecos.split(',', 1)
                if len(parts) >= 1 and parts[0]:
                    self.first_name = parts[0]
                if len(parts) >= 2 and parts[1]:
                    self.last_name = parts[1]
        except Exception:
            logging.exception(f"Failed to fetch name from comment for '{self.username}'",
                              extra={"id": "User Management"})

    def _fetch_last_auth_attempt(self):
        """Fetch only the most recent successful authentication attempt"""
        cmd = f"""
        sudo grep '{AuthenticationConstants().loggingGroup}' /var/log/kiosk_auth.log* | 
        grep -i 'Authentication Attempt' | 
        grep -i 'Successful' | 
        grep -i '"{self.username}"' | 
        sort -r | 
        head -n 1
        """

        result = subprocess.run(
            cmd.replace('\n', ' '),
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0 or not result.stdout.strip():
            cmd_archived = f"""
            sudo zgrep '{AuthenticationConstants().loggingGroup}' /var/log/kiosk_auth.log.*.gz | 
            grep -i 'Authentication Attempt' | 
            grep -i 'Successful' | 
            grep -i '"{self.username}"' | 
            sort -r | 
            head -n 1
            """

            result_archived = subprocess.run(
                cmd_archived.replace('\n', ' '),
                shell=True,
                capture_output=True,
                text=True
            )

            if result_archived.returncode != 0 or not result_archived.stdout.strip():
                return

            result = result_archived

        line = result.stdout.strip()
        if not line:
            return

        # Extract the JSON part from the syslog entry
        json_match = re.search(r'\{.*\}', line)
        if not json_match:
            return

        json_data = json.loads(json_match.group(0))

        # Check if this is a successful authentication attempt for our user
        if (json_data.get('Category') == 'Authentication Attempt' and
                json_data.get('Action') == 'Successful' and
                json_data.get('Username') == self.username):
            self.last_login_timestamp = json_data.get('Timestamp')
            try:
                dt = datetime.fromisoformat(self.last_login_timestamp)
                self.last_login = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                self.last_login = self.last_login_timestamp

    def _fetch_password_info(self):
        """Fetch password information for the user using chage command"""
        result = subprocess.run(
            ['sudo', 'chage', '-l', self.username],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logging.info(f"Error: Could not get password information for '{self.username}'.",
                         extra={"id": "User Management"})

        output = result.stdout

        # Define the patterns to extract information
        patterns = {
            "last_changed": r"Last password change\s*:\s*(.+)",
            "password_expires": r"Password expires\s*:\s*(.+)",
            "password_inactive": r"Password inactive\s*:\s*(.+)",
            "account_expires": r"Account expires\s*:\s*(.+)",
            "min_days": r"Minimum number of days between password change\s*:\s*(\d+)",
            "max_days": r"Maximum number of days between password change\s*:\s*(\d+)",
            "warning_days": r"Number of days of warning before password expires\s*:\s*(\d+)"
        }

        # Extract attributes based on the patterns
        for attr, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                setattr(self, attr, match.group(1).strip())
            else:
                setattr(self, attr, None)

    def get_dict(self):
        """Return user attributes as a dictionary for PDF/CSV export"""
        return {
            'Username': self.username,
            'First Name': self.first_name,
            'Last Name': self.last_name,
            'Role': self.role.display_name,
            'Password Last Changed': self.last_changed,
            'Password Expires': self.password_expires,
            'Password Inactive': self.password_inactive,
            'Last Active': self.last_login,
        }
