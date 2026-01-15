#!/bin/bash

# Install packages
xargs -a apt_requirements.txt sudo apt install -y
sudo pip3 install reactivex --break-system-packages
sudo apt remove brltty unattended-upgrades -y

# Add user to dialout group
sudo usermod -a -G dialout kiosk

# Copy cron and system configuration files
sudo dos2unix -q ../ubuntu_settings/delete_old_files
sudo cp ../ubuntu_settings/delete_old_files /etc/cron.d
sudo dos2unix -q ../ubuntu_settings/aide_config
sudo cp ../ubuntu_settings/aide_config /etc/cron.d

# Copy udev rules
sudo dos2unix -q ../ubuntu_settings/52-usb.rules
sudo cp ../ubuntu_settings/52-usb.rules /etc/udev/rules.d/
sudo dos2unix -q ../ubuntu_settings/92-usb-input-no-powersave.rules
sudo cp ../ubuntu_settings/92-usb-input-no-powersave.rules /etc/udev/rules.d/

# Copy Python path configuration (check Python version)
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_PATH="/usr/local/lib/python${PYTHON_VERSION}/dist-packages"
if [ -d "$PYTHON_PATH" ]; then
    sudo dos2unix -q ../ubuntu_settings/desktop-app-paths.pth
    sudo cp ../ubuntu_settings/desktop-app-paths.pth "$PYTHON_PATH/"
    echo "Python path configured for version $PYTHON_VERSION"
else
    echo "Warning: Python path $PYTHON_PATH not found"
fi

# Copy logo
sudo cp ../media/squareLogo.PNG /usr/share/icons/

# Setup Plymouth boot splash theme
echo "Setting up Plymouth boot splash..."

# Ensure Plymouth is properly installed
sudo apt install plymouth plymouth-themes -y

# Copy skroot theme
sudo dos2unix -q ../ubuntu_settings/skroot/skroot.plymouth
sudo dos2unix -q ../ubuntu_settings/skroot/skroot.script
sudo cp ../ubuntu_settings/skroot /usr/share/plymouth/themes/ -R

# Copy ibi theme
sudo dos2unix -q ../ubuntu_settings/ibi/ibi.plymouth
sudo dos2unix -q ../ubuntu_settings/ibi/ibi.script
sudo cp ../ubuntu_settings/ibi /usr/share/plymouth/themes/ -R

# Copy wilson-wolf theme
sudo dos2unix -q ../ubuntu_settings/wilson-wolf/wilson-wolf.plymouth
sudo dos2unix -q ../ubuntu_settings/wilson-wolf/wilson-wolf.script
sudo cp ../ubuntu_settings/wilson-wolf /usr/share/plymouth/themes/ -R

# Detect theme from Version class
THEME=$(python3 -c "from src.resources.version.version import Version; print(Version().getTheme().value)")
echo "Detected theme: $THEME"

# Set theme using Plymouth commands
sudo plymouth-set-default-theme "$THEME"

# Configure Plymouth to work better with LightDM
sudo mkdir -p /etc/systemd/system/lightdm.service.d
sudo tee /etc/systemd/system/lightdm.service.d/plymouth.conf > /dev/null << 'EOF'
[Unit]
After=plymouth-quit-wait.service
Wants=plymouth-quit-wait.service

[Service]
ExecStartPre=/bin/sleep 2
EOF
sudo mkdir -p /etc/systemd/system/plymouth-quit-wait.service.d
sudo dos2unix -q ../ubuntu_settings/plymouth-timeout.conf
sudo cp ../ubuntu_settings/plymouth-timeout.conf /etc/systemd/system/plymouth-quit-wait.service.d


# Update initramfs to include the new theme
sudo update-initramfs -u

# Trigger udev rules
sudo udevadm trigger --attr-match=subsystem=usb

echo ""
echo "Installation complete!"
echo "Plymouth theme: $(sudo plymouth-set-default-theme)"