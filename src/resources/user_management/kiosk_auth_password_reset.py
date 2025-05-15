#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import syslog
from datetime import datetime


def change_user_password(admin_username, username, new_password):
    """Change a user's password and log the attempt via syslog."""
    logAuthAction("Password Reset", "Initiated", username, admin_username)
    try:
        check_user_cmd = ["id", username]
        user_result = subprocess.run(check_user_cmd, capture_output=True, text=True)
        if user_result.returncode != 0:
            return {"success": False, "message": f"User '{username}' does not exist"}

        process = subprocess.Popen(
            "chpasswd",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=f"{username}:{new_password}")

        if process.returncode != 0:
            logAuthAction("Password Reset", "Failed", username, admin_username)
            return {"success": False, "message": f"Failed to change password: {stderr}"}

        logAuthAction(
            "Password Reset",
            "Successful",
            username,
            authorizer=admin_username,
            result=f"Password has been reset for '{username}'",
        )
        return {"success": True, "message": f"Password for '{username}' changed successfully"}
    except json.JSONDecodeError:
        logAuthAction("Password Reset", "Failed", username, admin_username)
        return {"success": False, "message": "Invalid JSON input"}
    except Exception as e:
        logAuthAction("Password Reset", "Failed", username, admin_username)
        return {"success": False, "message": f"Error: {str(e)}"}


def logAuthAction(category, action, username, authorizer=None, result=None):
    try:
        """Log user authentication actions in JSON format for Ubuntu kiosk_auth.log"""
        syslog.openlog("kiosk_users", 0, syslog.LOG_LOCAL0)

        # Create log data structure
        log_data = {
            "Category": category,
            "Action": action,
            "Username": username,
            "Timestamp": datetime.now().isoformat(timespec='seconds')
        }
        if authorizer:
            log_data["Authorizer"] = authorizer
        if result:
            log_data["Result"] = result

        # Convert to JSON string and log
        log_message = json.dumps(log_data, separators=(',', ':'))
        syslog.syslog(syslog.LOG_INFO, log_message)
    except:
        pass
    finally:
        syslog.closelog()


if __name__ == "__main__":
    input_data = sys.stdin.read().strip()

    try:
        auth_data = json.loads(input_data)
        username = auth_data.get('username', '')
        admin_username = auth_data.get('adminUsername', '')
        new_password = auth_data.get('newPassword', '')

        if not username or not new_password or not admin_username:
            print(json.dumps({"success": False, "error": "Missing arguments"}))
            sys.exit(1)

        result = change_user_password(admin_username, username, new_password)
        print(json.dumps(result))
        sys.exit(0 if result else 1)
    except Exception as e:
        print(json.dumps({"success": False, "message": str(e)}))
        sys.exit(1)
    finally:
        syslog.closelog()
