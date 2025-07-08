#!/bin/bash
# Kiosk startup script for Raspberry Pi OS
# Disable screen blanking and power management
xset s off
xset -dpms
xset s noblank
xsetroot -solid black


unclutter -idle 1 -root &
cd /home/kiosk/.local/DesktopApp/src/app || exit

# Optimize OS for python application
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1
export GDK_RENDERING=image
export QT_X11_NO_MITSHM=1

# Start the Python kiosk application with auto-restart
while true; do
    python3 main.py
    echo "Kiosk app exited, restarting in 3 seconds..."
    sleep 3
done