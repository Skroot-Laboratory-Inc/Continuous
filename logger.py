import logging
import os
import shutil
from datetime import datetime


def loggerSetup(location, version):
    if not os.path.exists(os.path.dirname(location)):
        os.mkdir(os.path.dirname(location))
    if not os.path.exists(location):
        open(location, 'w+').close()
    elif os.path.getsize(location) > 100000:
        # log is greater than 100 kB, make a copy and create a new one
        shutil.copy(location, f"{location[:-4]}_{datetime.now().date()}.txt")
        open(location, 'w+').close()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(location)
        ]
    )
    logging.getLogger().addFilter(DuplicateFilter())
    logging.captureWarnings(True)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger('s3transfer').setLevel(logging.ERROR)
    logging.info(f'Logger Setup {version}')
    return


def info(infoText):
    logging.info(infoText)


def exception(exceptionText):
    logging.exception(exceptionText)


class DuplicateFilter(logging.Filter):
    def __init__(self):
        self.consecutive_repeats = 0
        self.consecutive_repeats_warning = 100
        self.last_log = ""

    def filter(self, record):
        # add other fields if you need more granular comparison, depends on your app
        current_log = (record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            self.consecutive_repeats = 0
            return True
        self.consecutive_repeats += 1
        if self.consecutive_repeats % self.consecutive_repeats_warning == 0:
            logging.warning(f"{self.last_log} recorded {self.consecutive_repeats_warning} times in a row.")
        return False