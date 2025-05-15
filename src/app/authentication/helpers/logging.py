import csv
import glob
import json
import logging
import platform
import re
import subprocess
from datetime import datetime

from src.app.authentication.helpers.exceptions import AuthLogsNotFound, AideLogsNotFound
from src.app.helper_methods.pdf_helpers import createPdf

if platform.system() == "Linux":
    import syslog

from src.app.authentication.helpers.constants import AuthenticationConstants


def logAuthAction(category, action, username, result=None, authorizer=None, extra=None):
    try:
        if platform.system() == "Linux":
            """Log user authentication actions in JSON format for Ubuntu kiosk_auth.log"""
            syslog.openlog(AuthenticationConstants().loggingGroup, 0, syslog.LOG_LOCAL0)

            # Create log data structure
            log_data = {
                "Category": category,
                "Action": action,
                "Username": username,
                "Timestamp": datetime.now().isoformat(timespec='seconds')
            }
            if authorizer:
                log_data["Authorizer"] = authorizer
            if result:
                log_data["Result"] = result
            if extra:
                log_data["Extra"] = extra

            # Convert to JSON string and log
            log_message = json.dumps(log_data, separators=(',', ':'))
            syslog.syslog(syslog.LOG_INFO, log_message)
    except:
        logging.exception("Failed to create authorization logs.")
    finally:
        if platform.system() == "Linux":
            syslog.closelog()


def parseGrepRecords(grepCommand: str):
    process = subprocess.Popen(grepCommand, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    output, _ = process.communicate()

    # Parse the logs
    records = []
    for line in output.splitlines():
        json_match = re.search(r'{.*}', line)
        if json_match:
            try:
                json_data = json.loads(json_match.group(0))
                records.append(json_data)
            except json.JSONDecodeError:
                continue
    return records


def extractAuthLogs(search_term, output_csv, output_pdf, adminUser):
    logAuthAction("Auth Log Export", "Initiated", adminUser)
    if platform.system() == "Linux":
        # Run grep command to extract relevant logs
        grepCommand = f"sudo grep \"{search_term}\" /var/log/kiosk_auth.log* | sort -r"
        records = parseGrepRecords(grepCommand)
        grep_command = f"sudo zgrep \"{search_term}\" /var/log/kiosk_auth.log.*.gz | sort -r"
        compressedRecords = parseGrepRecords(grep_command)
        allRecords = records + compressedRecords
        # Write to CSV
        if allRecords:
            # Create ordered fieldnames with username first
            fieldnames = ["Timestamp", "Username", "Authorizer", "Category", "Action", "Result", "Extra"]
            data = []

            with open(output_csv, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(allRecords)

            with open(output_csv, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    data.append(row)

            createPdf(data,
                      output_pdf,
                      "Authorization Logs",
                      adminUser,
                      isLandscape=True,
                      )

            logAuthAction("Auth Log Export", "Successful", adminUser, extra=f"{len(records)} records found.")
        else:
            logAuthAction("Auth Log Export", "Failed", adminUser, extra=f"No records found.")
            raise AuthLogsNotFound()


def extractAideLogs(outputDir, adminUser):
    logAuthAction("AIDE Log Export", "Initiated", adminUser)
    if platform.system() == "Linux":
        aideLogs = glob.glob(f'{AuthenticationConstants().aideLogsDir}/aide-weekly-summary-*.log')
        if aideLogs:
            for logFile in aideLogs:
                result = subprocess.run(["sudo", "cp", logFile, outputDir],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                if result.returncode != 0:
                    raise AideLogsNotFound()
            logAuthAction("AIDE Log Export", "Successful", adminUser, extra=f"{len(aideLogs)} weeks of logs found.")
        else:
            logAuthAction("AIDE Log Export", "Failed", adminUser)
            raise AideLogsNotFound()
