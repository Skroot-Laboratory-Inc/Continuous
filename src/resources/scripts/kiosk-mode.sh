#!/bin/bash
sudo dos2unix ../kiosk_settings/kiosk.desktop
sudo cp ../kiosk_settings/kiosk.desktop /usr/share/xsessions
sudo dos2unix ../kiosk_settings/kiosk
sudo cp ../kiosk_settings/kiosk /var/lib/AccountsService/users
sudo dos2unix ../kiosk_settings/kiosk.session
sudo cp ../kiosk_settings/kiosk.session /usr/share/gnome-session/sessions
sudo dos2unix ../kiosk_settings/kiosk-shell.desktop
sudo cp ../kiosk_settings/kiosk-shell.desktop /usr/share/applications
sudo dos2unix ../kiosk_settings/kiosk.conf
sudo cp ../kiosk_settings/kiosk.conf /etc/gdm3/custom.conf
sudo dos2unix ../kiosk_settings/lcd_firmware_config.txt
sudo cp ../kiosk_settings/lcd_firmware_config.txt /boot/firmware/config.txt
sudo dos2unix ../kiosk_settings/kiosk-auto-login.conf
sudo cp ../kiosk_settings/kiosk-auto-login.conf /etc/gdm3/custom.conf
sudo cp ../kiosk_settings/kiosk-auto-login.conf /etc/systemd/sleep.conf
sudo dos2unix ../kiosk_settings/10-noblank.conf
sudo cp ../kiosk_settings/10-noblank.conf /etc/X11/xorg.conf.d
sudo mkdir /media/usb
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0
echo export MOZ_USE_XINPUT2=1 | sudo tee /etc/profile.d/use-xinput2.sh
sudo touch /var/log/kiosk_lockouts.log
sudo chown kiosk:kiosk /var/log/kiosk_lockouts.log
sudo chmod 0600 /var/log/kiosk_lockouts.log