import os

import certifi
from PyQt6.QtWidgets import QApplication

from logger import Logger
from window import Window


def run():
    logger = Logger()

    try:
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

        app = QApplication([])
        window = Window()
        window.show()
        app.exec()
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    run()
