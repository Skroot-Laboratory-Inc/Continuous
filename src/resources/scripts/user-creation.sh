#!/bin/bash

# Create user groups
sudo groupadd kiosk_administrators
sudo groupadd kiosk_users

# Copy user management files
sudo dos2unix -q ../user_management/kiosk_permissions
sudo cp ../user_management/kiosk_permissions /etc/sudoers.d/admins
sudo dos2unix -q ../user_management/kiosk_auth_check.py
sudo cp ../user_management/kiosk_auth_check.py /usr/local/bin
sudo dos2unix -q ../user_management/kiosk_auth_password_reset.py
sudo cp ../user_management/kiosk_auth_password_reset.py /usr/local/bin
sudo dos2unix -q ../user_management/kiosk_get_password_rotation.py
sudo cp ../user_management/kiosk_get_password_rotation.py /usr/local/bin
sudo dos2unix -q ../user_management/kiosk_update_password_rotation.py
sudo cp ../user_management/kiosk_update_password_rotation.py /usr/local/bin
sudo dos2unix -q ../user_management/kiosk_get_password_requirements.py
sudo cp ../user_management/kiosk_get_password_requirements.py /usr/local/bin
sudo dos2unix -q ../user_management/kiosk_update_password_requirements.py
sudo cp ../user_management/kiosk_update_password_requirements.py /usr/local/bin

# Copy system configuration files
sudo dos2unix -q ../user_management/default-password-reqs.defs
sudo cp ../user_management/default-password-reqs.defs /etc/login.defs
sudo dos2unix -q ../user_management/useradd
sudo cp ../user_management/useradd /etc/default
sudo dos2unix -q ../user_management/common-auth
sudo cp ../user_management/common-auth /etc/pam.d
sudo dos2unix -q ../user_management/common-password
sudo cp ../user_management/common-password /etc/pam.d
sudo dos2unix -q ../user_management/faillock.conf
sudo cp ../user_management/faillock.conf /etc/security
sudo dos2unix -q ../user_management/pwquality.conf
sudo cp ../user_management/pwquality.conf /etc/security
sudo dos2unix -q ../user_management/safe_chown.sh
sudo cp ../user_management/safe_chown.sh /usr/local/bin
sudo dos2unix -q ../user_management/login_settings
sudo cp ../user_management/login_settings /etc/pam.d/login

# Setup rsyslog for authentication logging
echo "Setting up rsyslog for authentication logging..."

# Install rsyslog if not present
if ! systemctl is-active --quiet rsyslog; then
    sudo apt install rsyslog -y
    sudo systemctl enable rsyslog
    sudo systemctl start rsyslog
fi

# Create rsyslog.d directory and copy configuration
sudo mkdir -p /etc/rsyslog.d
sudo dos2unix -q ../user_management/kiosk_logging.conf
sudo cp ../user_management/kiosk_logging.conf /etc/rsyslog.d/kiosk_auth.conf

# Create log file with proper permissions
sudo touch /var/log/kiosk_auth.log
sudo chown root:adm /var/log/kiosk_auth.log
sudo chmod 640 /var/log/kiosk_auth.log

# Setup log rotation
sudo dos2unix -q ../user_management/auth_log_rotation
sudo cp ../user_management/auth_log_rotation /etc/logrotate.d/auth-audit

# Restart rsyslog to apply configuration
sudo systemctl restart rsyslog

# Set file permissions
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

# Test the logging setup
logger -p local0.info "Kiosk authentication logging system initialized"

echo "User management and authentication logging setup complete!"
echo "Check /var/log/kiosk_auth.log for authentication events"