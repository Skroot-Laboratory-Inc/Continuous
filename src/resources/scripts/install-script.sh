#!/bin/bash
xargs -a apt_requirements.txt sudo apt install -y
sudo apt remove brltty unattended-upgrades -y
sudo usermod -a -G dialout kiosk
if ! grep -q "nomodeset" /boot/firmware/cmdline.txt; then
    sudo sed -i 's/$/ nomodeset/' /boot/firmware/cmdline.txt
fi
sudo dos2unix ../ubuntu_settings/delete_old_files
sudo cp ../ubuntu_settings/delete_old_files /etc/cron.d
sudo dos2unix ../ubuntu_settings/aide_config
sudo cp ../ubuntu_settings/aide_config /etc/cron.d
sudo dos2unix ../ubuntu_settings/desktopApp.desktop
sudo cp ../ubuntu_settings/desktopApp.desktop /home/kiosk/.local/share/applications
sudo chown kiosk:kiosk /home/kiosk/.local/share/applications/desktopApp.desktop
sudo dos2unix ../ubuntu_settings/52-usb.rules
sudo cp ../ubuntu_settings/52-usb.rules /etc/udev/rules.d/52-usb.rules
sudo dos2unix ../ubuntu_settings/92-usb-input-no-powersave.rules
sudo cp ../ubuntu_settings/92-usb-input-no-powersave.rules /etc/udev/rules.d/92-usb-input-no-powersave.rules
sudo dos2unix ../ubuntu_settings/desktop-app-paths.pth
sudo cp ../ubuntu_settings/desktop-app-paths.pth /usr/local/lib/python3.12/dist-packages
sudo cp ../media/squareLogo.PNG /usr/share/icons/squareLogo.PNG
sudo cp ../media/squareLogo.PNG /usr/share/plymouth/themes/spinner/bgrt-fallback.png
sudo rm /usr/share/plymouth/themes/spinner/watermark.png
sudo rm /usr/share/plymouth/ubuntu-logo.png
sudo udevadm trigger --attr-match=subsystem=usb