#!/bin/bash

# Pi OS LightDM Kiosk Mode Setup Script

echo "Setting up kiosk mode for Raspberry Pi OS with LightDM..."
sudo tee /etc/X11/xorg.conf.d/99-touchscreen-rotation.conf > /dev/null << 'EOF'
Section "Monitor"
    Identifier "DSI-2"
    Option "Rotate" "right"
EndSection

Section "InputClass"
    Identifier "Touch rotation 90"
    MatchIsTouchscreen "on"
    # Transformation matrix for 90-degree rotation
    Option "TransformationMatrix" "0 1 0 -1 0 1 0 0 1"
EndSection
EOF
add_boot_param() {
    local param="$1"
    if ! grep -q "$param" "/boot/firmware/cmdline.txt"; then
        sudo sed -i "s/$/ $param/" "/boot/firmware/cmdline.txt"
        echo "Added: $param"
    fi
}

# Add boot parameters
add_boot_param "nomodeset"
add_boot_param "video=DSI-2:720x1280@60,rotate=90"
add_boot_param "splash"
add_boot_param "quiet"
#add_boot_param "plymouth.rotation=90"
add_boot_param "plymouth.ignore-serial-consoles"
# Install required packages
sudo apt install lightdm unclutter xdotool -y

# Create kiosk startup script
sudo dos2unix ../kiosk_settings/start-kiosk.sh
sudo cp ../kiosk_settings/start-kiosk.sh /home/kiosk/
sudo chmod +x /home/kiosk/start-kiosk.sh
sudo chown kiosk:kiosk /home/kiosk/start-kiosk.sh

# Allow kiosk to run necessary commands
sudo adduser kiosk sudo

# Create X session file for kiosk mode
sudo dos2unix ../kiosk_settings/kiosk.desktop
sudo cp ../kiosk_settings/kiosk.desktop /usr/share/xsessions/

# Configure LightDM for autologin
sudo dos2unix ../kiosk_settings/lightdm.conf
sudo cp ../kiosk_settings/lightdm.conf /etc/lightdm/

# Create AccountsService user file
sudo mkdir -p /var/lib/AccountsService/users
sudo dos2unix ../kiosk_settings/kiosk
sudo cp ../kiosk_settings/kiosk /var/lib/AccountsService/users/

# Copy X11 configuration for screen blanking
sudo dos2unix ../kiosk_settings/10-noblank.conf
sudo cp ../kiosk_settings/10-noblank.conf /etc/X11/xorg.conf.d/

# Create directories and set permissions
sudo mkdir -p /media/usb
sudo touch /var/log/kiosk_lockouts.log
sudo chown kiosk:kiosk /var/log/kiosk_lockouts.log
sudo chmod 0600 /var/log/kiosk_lockouts.log

# Configure Mozilla/Firefox touch input
echo 'export MOZ_USE_XINPUT2=1' | sudo tee /etc/profile.d/use-xinput2.sh

# Enable LightDM
sudo systemctl enable lightdm

# Mask getty on tty1 to prevent terminal from showing
sudo systemctl mask getty@tty1.service
sudo systemctl mask getty@tty7.service

echo "Kiosk mode setup complete!"
echo "Reboot to start in kiosk mode."