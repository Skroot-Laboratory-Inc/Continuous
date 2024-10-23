#!bash
sudo apt-get install python3-pip -y &&
sudo python3 -m pip install --upgrade pip &&
pip install -r ./requirements.txt &&
sudo apt-get install python3-pil.imagetk libhidapi-dev scrot gnome-screenshot uhubctl -y &&
sudo apt remove brltty -y &&
sudo usermod -a -G dialout skroot &&
sudo cp ../delete_old_files /etc/cron.d &&
sudo cp ../52-usb.rules /etc/udev/rules.d/52-usb.rules &&
sudo cp ../92-usb-input-no-powersave.rules /etc/udev/rules.d/92-usb-input-no-powersave.rules &&
sudo udevadm trigger --attr-match=subsystem=usb