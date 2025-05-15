#!/bin/bash
sudo apt install aide -y
sudo dos2unix ../aide/aide.conf
sudo cp ../aide/aide.conf /etc/aide/aide.conf
sudo dos2unix ../aide/daily-aide-check.sh
sudo cp ../aide/daily-aide-check.sh /usr/local/bin/daily-aide-check.sh
sudo dos2unix ../aide/aide_log_rotation
sudo cp ../aide/aide_log_rotation /etc/logrotate.d/aide-audit
sudo dos2unix ../aide/weekly-aide-summary.sh
sudo cp ../aide/weekly-aide-summary.sh /usr/local/bin/weekly-aide-summary.sh
sudo aide --init --config=/etc/aide/aide.conf
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
sudo chmod +x /usr/local/bin/daily-aide-check.sh
sudo chmod +x /usr/local/bin/weekly-aide-summary.sh
sudo mkdir -p /var/log/aide
sudo chown root:root /var/log/aide
sudo chmod 0750 /var/log/aide