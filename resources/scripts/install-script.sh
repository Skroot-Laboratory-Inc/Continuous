#!bash
sudo apt-get install python3-pip -y
pip install -r ./requirements.txt
sudo apt-get install python3-pil.imagetk libhidapi-dev scrot -y
sudo apt remove brltty -y
sudo usermod -a -G dialout skroot