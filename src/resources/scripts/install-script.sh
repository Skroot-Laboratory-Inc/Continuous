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
sudo dos2unix ../ubuntu_settings/.xprofile
sudo cp ../ubuntu_settings/.xprofile /home/kiosk
sudo dos2unix ../ubuntu_settings/touchscreen-setup.sh
sudo cp ../ubuntu_settings/touchscreen-setup.sh /home/kiosk
sudo chmod +x /home/kiosk/touchscreen-setup.sh
sudo dos2unix ../ubuntu_settings/52-usb.rules
sudo cp ../ubuntu_settings/52-usb.rules /etc/udev/rules.d/52-usb.rules
sudo dos2unix ../ubuntu_settings/92-usb-input-no-powersave.rules
sudo cp ../ubuntu_settings/92-usb-input-no-powersave.rules /etc/udev/rules.d/92-usb-input-no-powersave.rules
sudo dos2unix ../ubuntu_settings/desktop-app-paths.pth
sudo cp ../ubuntu_settings/desktop-app-paths.pth /usr/local/lib/python3.12/dist-packages
sudo cp ../media/squareLogo.PNG /usr/share/icons/squareLogo.PNG
sudo dos2unix ../ubuntu_settings/skroot/skroot.plymouth
sudo dos2unix ../ubuntu_settings/skroot/skroot.script
sudo cp ../ubuntu_settings/skroot /usr/share/plymouth/themes/ -R
sudo update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/skroot/skroot.plymouth 120
sudo update-alternatives --set default.plymouth /usr/share/plymouth/themes/skroot/skroot.plymouth
sudo update-initramfs -u
sudo rm /usr/share/plymouth/themes/spinner/watermark.png
sudo touch /usr/share/plymouth/themes/spinner/watermark.png
sudo rm /usr/share/plymouth/ubuntu-logo.png
sudo udevadm trigger --attr-match=subsystem=usb