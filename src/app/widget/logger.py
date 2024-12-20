import logging
import os


def loggerSetup(location, version):
    if not os.path.exists(os.path.dirname(location)):
        os.mkdir(os.path.dirname(location))
    open(location, 'w+').close()
    logging.basicConfig(
        level=logging.INFO,
        format="%(id)s - %(asctime)s [%(levelname)s] %(message)s",
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
    logging.info(f'Logger Setup {version}', extra={"id": "global"})
    return


class DuplicateFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.consecutive_repeats = 0
        self.consecutive_repeats_warning = 100
        self.last_log = ""

    def filter(self, record: logging.LogRecord):
        # add other fields if you need more granular comparison, depends on your app
        current_log = (record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            self.consecutive_repeats = 0
            return True
        self.consecutive_repeats += 1
        if self.consecutive_repeats % self.consecutive_repeats_warning == 0:
            logging.warning(f"{self.last_log} recorded {self.consecutive_repeats_warning} times in a row.",
                            extra={"id": "global"})
        return False
