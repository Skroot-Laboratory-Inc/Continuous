#!/bin/bash

# Ensure we're running as root
if [ "$(id -u)" -ne 0 ]; then
   echo "This script must be run as root" >&2
   exit 1
fi

# Set up log directory and file with proper permissions
REPORT_DIR="/var/log/aide"
REPORT_FILE="$REPORT_DIR/daily-aide-check.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# Create log directory if it doesn't exist
if [ ! -d "$REPORT_DIR" ]; then
    mkdir -p "$REPORT_DIR"
    chmod 755 "$REPORT_DIR"
fi

# Create log file if it doesn't exist
if [ ! -f "$REPORT_FILE" ]; then
    touch "$REPORT_FILE"
    chmod 644 "$REPORT_FILE"
fi

# Add a separator for this run
echo -e "\n\n===========================================================" >> "$REPORT_FILE"
echo "=== AIDE Check Run: $DATE ===" >> "$REPORT_FILE"
echo "===========================================================" >> "$REPORT_FILE"

# Run the check and append output to the log file
/usr/bin/aide --check --config=/etc/aide/aide.conf >> "$REPORT_FILE" 2>&1

# Add a completion marker
echo "=== Check Completed: $(date) ===" >> "$REPORT_FILE"

# Update the database for the next run
/usr/bin/aide --init --config=/etc/aide/aide.conf
cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# For debugging
echo "AIDE check completed. Log appended to $REPORT_FILE"