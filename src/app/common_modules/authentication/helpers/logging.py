import glob
import json
import logging
import platform
import re
import subprocess
from datetime import datetime

from src.app.common_modules.authentication.helpers.exceptions import AuthLogsNotFound, AideLogsNotFound
from src.app.helper_methods.pdf_helpers import createPdf

if platform.system() == "Linux":
    import syslog

from src.app.common_modules.authentication.helpers.constants import AuthenticationConstants


def logAuthAction(category: str, action: str, username: str, result: str = None, authorizer: str = None, extra: str = None):
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


def getTimerangeFilter(startDate: datetime.date, endDate: datetime.date):
    """
    If both are None: no timestamp filtering
    If only min_timestamp: filters for records >= min_timestamp
    If only max_timestamp: filters for records <= max_timestamp
    If both provided: filters for records in the range

    :param startDate: The timestamp for the minimum date range searched
    :param endDate: The timestamp for the maximum date range searched
    :return: The string to append to a grep command to filter by dates
    """
    awkConditions = []
    if startDate is not None:
        awkConditions.append(f'substr($1,1,10) >= "{startDate.isoformat()}"')
    if endDate is not None:
        awkConditions.append(f'substr($1,1,10) <= "{endDate.isoformat()}"')

    if awkConditions:
        # sed was required before but causing issues now. It is required if the logs are filename:timestamp
        # return f" | sed 's/^[^:]*://' | awk '{' && '.join(awkConditions)}'"
        return f" | awk '{' && '.join(awkConditions)}'"
    else:
        return ""


def extractAuthLogs(search_term: str, output_pdf: str, adminUser: str, startDate: datetime.date, endDate: datetime.date):
    logAuthAction("Auth Log Export", "Initiated", adminUser)
    if platform.system() == "Linux":
        filterCmd = getTimerangeFilter(startDate, endDate)
        # Run grep command to extract relevant logs
        grepCommand = f"sudo grep -h \"{search_term}\" /var/log/kiosk_auth.log*{filterCmd} |  sort -r"
        logging.info(grepCommand, extra={"id": "grep"})
        records = parseGrepRecords(grepCommand)
        zgrepCommand = f"sudo zgrep -h \"{search_term}\" /var/log/kiosk_auth.log.*.gz{filterCmd} | sort -r"
        logging.info(zgrepCommand, extra={"id": "grep"})
        compressedRecords = parseGrepRecords(zgrepCommand)

        allRecords = records + compressedRecords
        if allRecords:
            fieldnames = ["Timestamp", "Username", "Authorizer", "Category", "Action", "Result", "Extra"]
            data = [fieldnames]
            for record in allRecords:
                row = [record.get(field, '-') for field in fieldnames]
                data.append(row)

            createPdf(data,
                      output_pdf,
                      f"Authorization Logs: {startDate} through {endDate}",
                      adminUser,
                      )

            logAuthAction("Auth Log Export", "Successful", adminUser, extra=f"{len(records)} records found.")
        else:
            logAuthAction("Auth Log Export", "Failed", adminUser, extra=f"No records found.")
            raise AuthLogsNotFound()


def extractAideLogs(outputDir: str, adminUser: str):
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
            logAuthAction("AIDE Log Export", "Successful", adminUser, extra=f"No logs found.")
