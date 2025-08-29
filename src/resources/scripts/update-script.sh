#!/bin/bash

# Update system and install dos2unix
sudo apt-get update
sudo apt install dos2unix

# Create .local directory structure for kiosk user
sudo mkdir -p /home/kiosk/.local/DesktopApp
sudo mkdir -p /home/kiosk/.local/temp
sudo mkdir -p /home/kiosk/.local/share/applications

# Remove old application files and copy new ones
sudo rm -rf /home/kiosk/.local/DesktopApp/src
sudo cp ../../../src /home/kiosk/.local/DesktopApp/ -R

# Set proper permissions for application files
sudo chmod -R 755 /home/kiosk/.local/DesktopApp
sudo chown -R kiosk:kiosk /home/kiosk/.local

# Convert line endings and run setup scripts
sudo dos2unix ./apt_requirements.txt
sudo dos2unix -q ./install-script.sh
sh install-script.sh

sudo dos2unix -q ./kiosk-mode.sh
sh kiosk-mode.sh

sudo dos2unix -q ./user-creation.sh
sh user-creation.sh

sudo dos2unix -q ./aide-configuration.sh
sh aide-configuration.sh

if ! sudo grep -q "dtparam=rtc_bbat_vchg" /boot/firmware/config.txt; then
    echo "dtparam=rtc_bbat_vchg=3000000" | sudo tee -a /boot/firmware/config.txt > /dev/null
fi