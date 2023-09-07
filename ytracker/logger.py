import os
import logging
from ytracker.constants import PACKAGE_NAME


class Logger:
    __slots__ = '_logger'

    _instance = None

    def __new__(cls, log_file: str | None = None):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._initialize_logger(cls._instance, log_file)
        return cls._instance

    def _initialize_logger(self, log_file: str | None = None):
        self._logger = logging.getLogger(PACKAGE_NAME)
        self._logger.setLevel(logging.DEBUG)

        if log_file is None:
            log_file = os.path.join(
                os.environ.get('HOME'),
                '.local',
                'share',
                PACKAGE_NAME,
                f'{PACKAGE_NAME}.log'
            )

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self._logger.addHandler(file_handler)

    def info(self, msg: str) -> None:
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        self._logger.warning(msg)

    def debug(self, msg: str) -> None:
        self._logger.debug(msg)

    def error(self, msg: str) -> None:
        self._logger.error(msg)

    def critical(self, msg: str) -> None:
        self._logger.critical(msg)
