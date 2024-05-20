import logging
import os


class Logger:
    def __init__(self, log_dir="logs", log_file="app.log"):
        os.makedirs(log_dir, exist_ok=True)
        logPath = os.path.join(log_dir, log_file)
        logging.basicConfig(
            filename=logPath,
            level=logging.ERROR,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.logger = logging.getLogger()

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
