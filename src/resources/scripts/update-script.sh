#!/bin/bash
sudo apt install dos2unix
sudo rm /home/kiosk/.local/DesktopApp/src -R
sudo cp ../../../src /home/kiosk/.local/DesktopApp/ -R
chmod -R 711 /home/kiosk/.local/DesktopApp
sudo chown -R kiosk:kiosk /home/kiosk/.local/DesktopApp
sudo dos2unix ./apt_requirements.txt
sudo dos2unix ./install-script.sh
sh install-script.sh
sudo dos2unix ./kiosk-mode.sh
sh kiosk-mode.sh
sudo dos2unix ./user-creation.sh
sh user-creation.sh
sudo dos2unix ./aide-configuration.sh
sh aide-configuration.sh