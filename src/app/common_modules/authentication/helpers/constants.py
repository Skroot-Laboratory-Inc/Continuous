class AuthenticationConstants:
    def __init__(self):
        self.systemAdminsUser = "sys_admin"
        self.adminGroup = "kiosk_administrators"
        self.userGroup = "kiosk_users"
        self.loggingGroup = "kiosk_users"
        self.defaultAuth = "true"
        self.aideLogsDir = "/var/log/aide"
        self.getPasswordPolicies = "/usr/local/bin/kiosk_get_password_rotation.py"
        self.getPasswordRequirements = "/usr/local/bin/kiosk_get_password_requirements.py"
        self.updatePasswordPolicies = "/usr/local/bin/kiosk_update_password_rotation.py"
        self.updatePasswordRequirements = "/usr/local/bin/kiosk_update_password_requirements.py"
        self.lockoutFile = '/var/log/kiosk_lockouts.log'
