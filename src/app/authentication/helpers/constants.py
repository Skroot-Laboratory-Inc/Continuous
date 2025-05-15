class AuthenticationConstants:
    def __init__(self):
        self.sudoersGroup = "sudo"
        self.adminGroup = "kiosk_administrators"
        self.userGroup = "kiosk_users"
        self.loggingGroup = "kiosk_users"
        self.authConfiguration = "auth_enabled"
        self.defaultAuth = "true"
        self.aideLogsDir = "/var/log/aide"
        self.getPasswordPolicies = "/usr/local/bin/kiosk_get_password_policy.py"
        self.updatePasswordPolicies = "/usr/local/bin/kiosk_update_password_policy.py"
        self.lockoutFile = '/var/log/kiosk_lockouts.log'
