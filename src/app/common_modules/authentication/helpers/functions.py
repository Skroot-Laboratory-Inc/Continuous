import json
import logging
import os
import platform
if platform.system() == "Linux":
    from pwquality import PWQSettings, PWQError
else:
    from pwquality_windows import PWQSettings, PWQError
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List

from src.app.common_modules.authentication.helpers.constants import AuthenticationConstants
from src.app.common_modules.authentication.helpers.exceptions import UserExistsException, UserDoesntExistException, \
    BadPasswordException, PamException, IncorrectPasswordException, PasswordExpired, SystemAdminException, \
    InsufficientPermissions, ResetPasswordException, RetireUserException, ModifyUserRoleException, \
    UserNotRetiredException
from src.app.common_modules.authentication.helpers.logging import logAuthAction
from src.app.common_modules.authentication.model.user import User
from src.app.common_modules.authentication.model.user_role import UserRole
from src.app.common_modules.authentication.password_policy_manager.password_rotation_manager import PasswordRotationManager
from src.app.widget import text_notification


def createKioskUser(user: str, passwd: str):
    if user_exists(user):
        raise UserExistsException()
    goodPassword, message = check_password_quality(user, passwd)
    if not goodPassword:
        raise BadPasswordException(message)
    encodedPasswd = subprocess.check_output(["mkpasswd", "-m", "sha-512", passwd]).decode().strip()

    process = subprocess.Popen([
        "sudo", "useradd",  # Create a user using user group privileges
        "-M",  # Do not create a home directory for the user
        "--system",  # Do not allow the user to sign in from the GUI
        "-p", encodedPasswd,  # Enter the hashed password
        "-G", AuthenticationConstants().userGroup,  # Add them to their permissions group
        user],  # Enter the username to create
        stdin=subprocess.PIPE)
    process.wait()
    if process.returncode == 0:
        addAgingParams(user)
    return process.returncode


def createKioskAdmin(user: str, passwd: str):
    if user_exists(user):
        raise UserExistsException()
    goodPassword, message = check_password_quality(user, passwd)
    if not goodPassword:
        raise BadPasswordException(message)
    encodedPasswd = subprocess.check_output(["mkpasswd", "-m", "sha-512", passwd]).decode().strip()
    process = subprocess.Popen([
        "sudo", "useradd",  # Create a user using user group privileges
        "-M",  # Do not create a home directory for the user
        "--system",  # Do not allow the user to sign in from the GUI
        "-p", encodedPasswd,  # Enter the hashed password
        "-G", AuthenticationConstants().adminGroup,  # Add them to their permissions group
        user],  # Enter the username to create
        stdin=subprocess.PIPE)
    process.wait()
    if process.returncode == 0:
        addAgingParams(user)
    return process.returncode


def addAgingParams(username: str):
    if platform.system() == "Linux":
        passwordPolicies = PasswordRotationManager()
        subprocess.run(['sudo', 'chage',
                        '-M', str(passwordPolicies.max_days),
                        '-I', str(passwordPolicies.inactive_days),
                        username],
                       capture_output=True, text=True)


def check_password_quality(username, password) -> (bool, str):
    try:
        pwq = PWQSettings()
        pwq.read_config()

        # Check the password quality - returns score or raises exception
        score = pwq.check(password, None, username)
        return True, ""
    except PWQError as e:
        error_code, message = e.args
        logging.info(f"Password rejected: {message}")
        return False, message


def user_exists(username):
    """Check if a user exists."""
    try:
        # getent will return 0 if user exists, non-zero otherwise
        result = subprocess.run(['getent', 'passwd', username],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        # If there's an error, assume user might exist to be safe
        return True


def validateUserCredentials(username: str, password: str):
    """ Checks that the correct username and password was entered for the signed-in user. """
    if platform.system() == "Linux":
        verify_credentials(username, password)


def isAdministrator(username):
    if platform.system() == "Linux":
        isAdmin = False
        try:
            output = subprocess.check_output(["groups", username], timeout=1).decode().strip()
            groups = output.split(" : ")[1].split(" ")
            if AuthenticationConstants().adminGroup in groups:
                isAdmin = True
        except:
            logging.exception("Failed to determine if user is an admin", extra={"id": "auth"})
    else:
        isAdmin = True
    return isAdmin


def isSystemAdmin(username):
    if platform.system() == "Linux":
        isSysAdmin = False
        try:
            output = subprocess.check_output(f"getent passwd {username}", shell=True).decode().strip()
            full_name = output.split(':')[4].split(',')[0]
            if full_name == "Administrator":
                isSysAdmin = True
        except:
            logging.exception("Failed to determine if user is a system admin", extra={"id": "auth"})
    else:
        isSysAdmin = True
    return isSysAdmin


def verify_credentials(username, password):
    # Prepare credentials as JSON to avoid command line exposure
    auth_data = json.dumps({"username": username, "password": password})

    # Call the helper_methods script with elevated privileges
    process = subprocess.Popen(
        ["sudo", "python3", "/usr/local/bin/kiosk_auth_check.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Pass credentials via stdin
    stdout, stderr = process.communicate(input=auth_data, timeout=5)

    # Parse the response
    result = json.loads(stdout)
    success = result.get("success", True)
    reason = result.get("reason", "")
    code = result.get("code", "")
    if success:
        if code == 12:
            raise PasswordExpired()
    if not success:
        if "User has been locked out for 10 minutes" in reason:
            addLockedOutUser(username)
            raise PamException(f"{reason}")
        if code == 6:
            raise IncorrectPasswordException()
        else:
            raise PamException(f"{reason}")


def authorizedToReset(authorizer: str, resetUserTarget: str) -> bool:
    """
    Returns a bool of whether the user is authorized to retire another user.

    Parameters:
    -----------
    authorizer : str
        The username of the authorizing user/admin
    retireUserTarget : str
        The user/admin that the authorizer is trying to retire

    Returns:
    --------
    bool
        Whether the `authorizer` is authorized to reset the password of `resetUserTarget` or not.

    Raises:
    -------
    SystemAdminException
        If the `authorizer` is trying to reset the password of the system admin and is not the system admin
    InsufficientPermissions
        If the `authorizer` is not authorized to reset the password of `resetUserTarget`
    """
    authorizerRole = getRole(authorizer)
    resetUserRole = getRole(resetUserTarget)
    if authorizer == resetUserTarget:
        #  You can reset your own password.
        return True
    if authorizerRole == UserRole.USER:
        #  Users cannot reset anyone else's password
        raise InsufficientPermissions("Users can only reset their own password")
    if resetUserRole == UserRole.SYSTEM_ADMIN:
        #  Only the system admin can reset their own password
        raise SystemAdminException("You cannot reset the system administrators password.")
    if authorizerRole < resetUserRole:
        #  You cannot reset users with higher permissions than yourself
        raise InsufficientPermissions(f"You are not authorized to reset the password for {resetUserTarget}")
    return True


def authorizedToRetire(authorizer: str, retireUserTarget: str) -> bool:
    """
    Returns a bool of whether the user is authorized to retire another user.

    Parameters:
    -----------
    authorizer : str
        The username of the authorizing user/admin
    retireUserTarget : str
        The user/admin that the authorizer is trying to retire

    Returns:
    --------
    bool
        Whether the `authorizer` is authorized to retire of `retireUserTarget` or not.

    Raises:
    -------
    SystemAdminException
        If the `authorizer` is trying to retire the system administrator
    InsufficientPermissions
        If the `authorizer` is not authorized to retire the `retireUserTarget`
    """
    authorizerRole = getRole(authorizer)
    retireUserRole = getRole(retireUserTarget)
    if retireUserRole == UserRole.SYSTEM_ADMIN:
        #  Nobody can retire the system administrator
        raise SystemAdminException("The system administrator cannot be retired.")
    if authorizer == retireUserTarget:
        #  You can retire yourself
        return True
    if authorizerRole == UserRole.USER:
        #  A user cannot retire anybody else
        raise InsufficientPermissions(f"Users can only retire themselves")
    if authorizerRole < retireUserRole:
        #  You cannot retire users with higher permissions than yourself
        raise InsufficientPermissions(f"You are not authorized to retire {retireUserTarget}")
    return True


def resetPassword(authorizer: str, resetUserTarget: str, newPassword) -> (bool, str):
    goodPassword, message = check_password_quality(resetUserTarget, newPassword)
    if not goodPassword:
        raise BadPasswordException(message)
    if authorizedToReset(authorizer, resetUserTarget):
        auth_data = json.dumps({"username": resetUserTarget, "adminUsername": authorizer, "newPassword": newPassword})

        process = subprocess.Popen(
            ["sudo", "python3", "/usr/local/bin/kiosk_auth_password_reset.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=auth_data, timeout=1)
        result = json.loads(stdout)

        if process.returncode != 0:
            logging.info(
                f"Process did not return code 0: Code {process.returncode}, output: {stdout}", extra={"id": "auth"})
            raise ResetPasswordException(result.get("message", ""))

        if result.get("success", False):
            text_notification.setText(f"Password reset for {resetUserTarget} was successful.")
        else:
            raise ResetPasswordException(result.get("message", ""))


def getRole(username: str) -> UserRole:
    if username in [user.username for user in getAdmins()]:
        return UserRole.ADMIN
    elif username in [user.username for user in getUsers()]:
        return UserRole.USER
    elif username in getSystemAdmin():
        return UserRole.SYSTEM_ADMIN
    else:
        raise UserDoesntExistException(f"`{username} is not in the system.")


def getAdmins() -> List[User]:
    if platform.system() == "Linux":
        import grp
        users = grp.getgrnam(AuthenticationConstants().adminGroup).gr_mem
    else:
        users = [
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
            "test_admin1",
            "test_admin2",
        ]
    return [User(username, True) for username in users]


def getSystemAdmin() -> List[str]:
    if platform.system() == "Linux":
        users = [AuthenticationConstants().systemAdminsUser]
    else:
        users = ["Skroot", "test_sudoer2"]
    return users


def getUsers() -> List[User]:
    if platform.system() == "Linux":
        import grp
        users = grp.getgrnam(AuthenticationConstants().userGroup).gr_mem
    else:
        users = ["test_user1", "test_user2"]
    return [User(username) for username in users]


def retireUser(authorizer: str, retireUserTarget: str):
    if not user_exists(retireUserTarget):
        raise UserDoesntExistException()
    logAuthAction("Retire User", "Initiated", retireUserTarget, authorizer=authorizer)
    if authorizedToRetire(authorizer, retireUserTarget):
        process = subprocess.Popen(["sudo", "usermod", "-L", retireUserTarget])
        process.wait()
        if process.returncode == 0:
            logAuthAction(
                "Retire User",
                "Successful",
                retireUserTarget,
                authorizer=authorizer,
                result=f"'{retireUserTarget}' has been retired",
            )
        else:
            logAuthAction("Retire User", "Failed", retireUserTarget, authorizer=authorizer)
            logging.info(f"Failed to delete `{retireUserTarget}` by {authorizer}. Return code: {process.returncode}",
                         extra={"id": "auth"})
            raise RetireUserException(f"`{retireUserTarget}` not deleted.")


def modifyRole(authorizer: str, modifyUser: str, newRole: UserRole):
    if not user_exists(modifyUser):
        raise UserDoesntExistException()
    logAuthAction("Modify User", "Initiated", modifyUser, authorizer=authorizer)
    if newRole == UserRole.USER:
        addGroup = AuthenticationConstants().userGroup
        removeGroup = AuthenticationConstants().adminGroup
    elif newRole == UserRole.ADMIN:
        addGroup = AuthenticationConstants().adminGroup
        removeGroup = AuthenticationConstants().userGroup
    else:
        raise ModifyUserRoleException("New role is not an admin or user.")
    removeProcess = subprocess.Popen(["sudo", "gpasswd", "-d", modifyUser, removeGroup])
    removeProcess.wait()
    addProcess = subprocess.Popen(["sudo", "gpasswd", "-a", modifyUser, addGroup])
    addProcess.wait()
    if addProcess.returncode == 0 and removeProcess.returncode == 0:
        logAuthAction(
            "Modify User",
            "Successful",
            modifyUser,
            authorizer=authorizer,
            result=f"'{modifyUser}' is now {newRole.prefixed_display_name}",
        )
    else:
        logAuthAction("Modify User", "Failed", modifyUser, authorizer=authorizer)
        logging.info(
            f"Failed to change role for {modifyUser} to {newRole.display_name} by {authorizer}. "
            f"Return codes: add:{addProcess.returncode} and remove:{removeProcess.returncode}",
            extra={"id": "auth"},
        )
        raise ModifyUserRoleException(f"`{modifyUser}` not changed to {newRole.display_name}.")


def restoreUser(adminUsername: str, username: str) -> (bool, str):
    if not user_exists(username):
        raise UserDoesntExistException()
    if not isUserRetired(username):
        raise UserNotRetiredException()
    logAuthAction("Restore User", "Initiated", username, authorizer=adminUsername)
    process = subprocess.Popen(["sudo", "usermod", "-U", username])
    process.wait()
    if process.returncode == 0:
        logAuthAction(
            "Restore User",
            "Successful",
            username,
            authorizer=adminUsername,
            result=f"'{username}' has been restored.",
        )
        return True, ""
    else:
        logAuthAction("Restore User", "Failed", username, authorizer=adminUsername)
        logging.info(f"Failed to restore `{username}` by {adminUsername}. Return code: {process.returncode}",
                     extra={"id": "auth"})
        text_notification.setText(f"Failed to restore system user `{username}`.")
        return False, f"`{username}` not restored."


def isUserRetired(username: str):
    result = subprocess.run(
        ['sudo', 'passwd', '-S', username],
        capture_output=True,
        text=True,
        check=True
    )

    output_parts = result.stdout.strip().split()
    if len(output_parts) >= 2:
        status = output_parts[1]
        return status == 'L'
    else:
        return False


def addLockedOutUser(username: str):
    lockoutFile = AuthenticationConstants().lockoutFile
    user_already_logged = False
    if os.path.exists(lockoutFile) and os.path.getsize(lockoutFile) > 0:
        with open(lockoutFile, 'r') as f:
            if username in f.read().splitlines():
                user_already_logged = True

    # Only add the username if it's not already in the file
    if not user_already_logged:
        with open(lockoutFile, 'a') as f:
            f.write(f"'{username}' locked out on {datetime.now().isoformat(timespec='minutes')}\n")
        logging.info(f"LOCKOUT: `{username}` has been locked out")


def getLockedOutUsers() -> List[str]:
    lockoutFile = AuthenticationConstants().lockoutFile
    if not os.path.exists(lockoutFile) or os.path.getsize(lockoutFile) == 0:
        return []

    with open(lockoutFile, 'r') as f:
        lockouts = f.readlines()
    return lockouts


def clearLockedOutUsers():
    with open(AuthenticationConstants().lockoutFile, 'w') as f:
        pass


def setFileOwner(filePath: str, newOwner: str):
    try:
        if newOwner != "":
            # Sets the file as read only
            subprocess.run(["sudo", "chmod", "444", filePath], check=True)
            # Sets the owner to the user passed in
            subprocess.run(["sudo", "sh", "/usr/local/bin/safe_chown.sh", newOwner, filePath], check=True)
            # Sets the file as immutable
            subprocess.run(["sudo", "chattr", "+i", filePath], check=True)
            logging.info(f"Successfully changed owner of {filePath} to {newOwner}", extra={"id": "auth"})
    except subprocess.CalledProcessError as e:
        logging.info(f"Failed to change ownership of {filePath} to {newOwner}: {e}", extra={"id": "auth"})


def getFileOwner(filename: str) -> str:
    if platform.system() == "Linux":
        filePath = Path(filename)
        statInfo = filePath.stat()
        uid = statInfo.st_uid
        import pwd
        username = pwd.getpwuid(uid).pw_name
        return username
    else:
        return "Windows User"
