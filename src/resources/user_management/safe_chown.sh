#!/bin/bash
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 new_owner file"
    exit 1
fi

NEW_OWNER="$1"
FILE="$2"

# Ensure the file exists
if [ ! -e "$FILE" ]; then
    echo "Error: File does not exist"
    exit 1
fi

# Get current user running the command
CURRENT_USER=${SUDO_USER:-$(whoami)}  # Defaults to whoami if not run via sudo

# Check if the current user owns the file
if [ "$(stat -c '%U' "$FILE")" != "$CURRENT_USER" ]; then
    echo "Error: You do not own this file"
    exit 1
fi

# Run chown as sudo
sudo /bin/chown "$NEW_OWNER" "$FILE"
