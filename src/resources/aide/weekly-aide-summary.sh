#!/bin/bash

REPORT_DIR="/var/log/aide"
DAILY_LOG="$REPORT_DIR/daily-aide-check.log"
WEEK_NUM=$(date +"%Y-W%W")
SUMMARY_LOG="$REPORT_DIR/aide-weekly-summary-$WEEK_NUM.log"

echo "AIDE Weekly Summary: $WEEK_NUM" > "$SUMMARY_LOG"
echo "Generated: $(date)" >> "$SUMMARY_LOG"
echo "=================================================" >> "$SUMMARY_LOG"

# Extract changes detected during the week
echo "Changes detected this week:" >> "$SUMMARY_LOG"
grep -A 5 "Changed entries:" "$DAILY_LOG" | grep -v "^--$" >> "$SUMMARY_LOG"

# Extract any errors
echo -e "\nErrors encountered:" >> "$SUMMARY_LOG"
grep -i "error\|warning\|fail" "$DAILY_LOG" >> "$SUMMARY_LOG"

# Create a signature to maintain 21 CFR Part 11 compliance
echo -e "\n=================================================" >> "$SUMMARY_LOG"
echo "Log integrity hash: $(md5sum "$DAILY_LOG" | cut -d' ' -f1)" >> "$SUMMARY_LOG"
echo "End of weekly report" >> "$SUMMARY_LOG"

# Set proper permissions
chmod 644 "$SUMMARY_LOG"