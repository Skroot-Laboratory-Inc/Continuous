#!/bin/bash
sudo groupadd kiosk_administrators
sudo groupadd kiosk_users
sudo dos2unix ../user_management/kiosk_permissions
sudo cp ../user_management/kiosk_permissions /etc/sudoers.d/admins
sudo dos2unix ../user_management/kiosk_auth_check.py
sudo cp ../user_management/kiosk_auth_check.py /usr/local/bin
sudo dos2unix ../user_management/kiosk_auth_password_reset.py
sudo cp ../user_management/kiosk_auth_password_reset.py /usr/local/bin
sudo dos2unix ../user_management/kiosk_get_password_rotation.py
sudo cp ../user_management/kiosk_get_password_rotation.py /usr/local/bin
sudo dos2unix ../user_management/kiosk_update_password_rotation.py
sudo cp ../user_management/kiosk_update_password_rotation.py /usr/local/bin
sudo dos2unix ../user_management/kiosk_get_password_requirements.py
sudo cp ../user_management/kiosk_get_password_requirements.py /usr/local/bin
sudo dos2unix ../user_management/kiosk_update_password_requirements.py
sudo cp ../user_management/kiosk_update_password_requirements.py /usr/local/bin
sudo dos2unix ../user_management/default-password-reqs.defs
sudo cp ../user_management/default-password-reqs.defs /etc/login.defs
sudo dos2unix ../user_management/useradd
sudo cp ../user_management/useradd /etc/default
sudo dos2unix ../user_management/common-auth
sudo cp ../user_management/common-auth /etc/pam.d
sudo dos2unix ../user_management/common-password
sudo cp ../user_management/common-password /etc/pam.d
sudo dos2unix ../user_management/pwhistory.conf
sudo cp ../user_management/pwhistory.conf /etc/security
sudo dos2unix ../user_management/faillock.conf
sudo cp ../user_management/faillock.conf /etc/security
sudo dos2unix ../user_management/pwquality.conf
sudo cp ../user_management/pwquality.conf /etc/security
sudo dos2unix ../user_management/kiosk_logging.conf
sudo cp ../user_management/kiosk_logging.conf /etc/rsyslog.d/kiosk_auth.conf
sudo dos2unix ../user_management/auth_log_rotation
sudo cp ../user_management/auth_log_rotation /etc/logrotate.d/auth-audit
sudo dos2unix ../user_management/safe_chown.sh
sudo cp ../user_management/safe_chown.sh /usr/local/bin
sudo dos2unix ../user_management/login_settings
sudo cp ../user_management/login_settings /etc/pam.d/login
sudo chmod 440 /etc/sudoers.d/admins
sudo chmod 755 /var/log
sudo chmod 700 /usr/local/bin/kiosk_auth_check.py
sudo chmod 700 /usr/local/bin/kiosk_auth_password_reset.py
sudo chmod 755 /usr/local/bin/kiosk_get_password_rotation.py
sudo chmod 755 /usr/local/bin/kiosk_get_password_requirements.py
sudo chmod 700 /usr/local/bin/kiosk_update_password_rotation.py
sudo chmod 700 /usr/local/bin/kiosk_update_password_requirements.py
sudo chmod 700 /usr/local/bin/safe_chown.sh
sudo chown root:root /usr/local/bin/kiosk_auth_check.py
sudo chown root:root /usr/local/bin/kiosk_auth_password_reset.py
sudo chown root:root /usr/local/bin/safe_chown.sh
