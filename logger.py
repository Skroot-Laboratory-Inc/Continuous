import logging
import os


def loggerSetup(location, version):
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    try:
        logFile = open(location, 'w+')
    except:
        os.mkdir(os.path.dirname(location))
        logFile = open(location, 'w+')
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
