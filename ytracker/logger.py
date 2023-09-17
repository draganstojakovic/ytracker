import os
import logging


class Logger:
    __slots__ = '_logger',

    def __init__(self, package_name: str, log_file_path: str | None = None) -> None:
        self._logger = logging.getLogger(package_name)
        self._logger.setLevel(logging.DEBUG)
        if log_file_path is None:
            log_file_path = os.path.join(
                os.environ.get('HOME'),
                '.local',
                'share',
                package_name,
                f'{package_name}.log'
            )
        file_handler = logging.FileHandler(log_file_path)
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
