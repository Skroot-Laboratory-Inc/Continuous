import logging
import os
import shutil
from datetime import datetime


def loggerSetup(location, version):
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if not os.path.exists(os.path.dirname(location)):
        os.mkdir(os.path.dirname(location))
    if not os.path.exists(location):
        open(location, 'w+').close()
    elif os.path.getsize(location) > 50000000:
        # log is greater than 50 MB, make a copy and create a new one
        shutil.copy(location, f"{location[:-4]}_{datetime.now().date()}.txt")
        open(location, 'w+').close()
    fh = logging.FileHandler(location)
    logging.captureWarnings(True)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logger.addHandler(fh)
    logger.info(f'Logger Setup {version}')
    return


def info(infoText):
    logger.info(infoText)


def exception(exceptionText):
    logger.exception(exceptionText)
