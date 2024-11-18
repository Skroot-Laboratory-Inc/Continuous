#!bash
sudo apt-get install python3-pip -y || true &&
sudo python3 -m pip install --upgrade pip || true &&
pip install -r ./requirements.txt || true &&
sudo apt-get install python3-pil.imagetk libhidapi-dev scrot gnome-screenshot uhubctl -y || true &&
sudo apt remove brltty -y || true &&
sudo usermod -a -G dialout skroot || true &&
sudo cp ../delete_old_files /etc/cron.d || true &&
sudo cp ../52-usb.rules /etc/udev/rules.d/52-usb.rules || true &&
sudo cp ../92-usb-input-no-powersave.rules /etc/udev/rules.d/92-usb-input-no-powersave.rules || true &&
sudo udevadm trigger --attr-match=subsystem=usb || true