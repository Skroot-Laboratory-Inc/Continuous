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
sudo dos2unix ./install-script.sh
sh install-script.sh

sudo dos2unix ./kiosk-mode.sh
sh kiosk-mode.sh

sudo dos2unix ./user-creation.sh
sh user-creation.sh

sudo dos2unix ./aide-configuration.sh
sh aide-configuration.sh