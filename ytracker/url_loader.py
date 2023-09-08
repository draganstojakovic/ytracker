import os
import re
from ytracker.constants import PACKAGE_NAME
from ytracker.logger import Logger


class UrlLoader:
    __slots__ = '_file_path', '_urls', '_invalid_urls', '_logger'

    def __init__(self, file_path: str | None = None):
        self._logger = Logger()
        self._urls: list = []
        self._invalid_urls: list = []

        if file_path is None:
            self._file_path: str = os.path.join(
                os.environ.get('HOME'),
                '.local',
                'share',
                PACKAGE_NAME,
                'urls.txt'
            )
        else:
            self._file_path = file_path

        self._set_valid_urls()
        self._assert_urls()
        self._assert_invalid_urls()

    @classmethod
    def is_valid_youtube_url(cls, url: str) -> bool:
        return re.match(r'https://www\.youtube\.com/@[^/]+', url) is not None

    @property
    def urls(self) -> list[str]:
        return self._urls

    def _load_lines_from_file(self) -> list[str] | list[None]:
        try:
            with open(self._file_path, 'r') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            self._logger.critical(f'Urls file not found.')
            raise SystemExit()
        except IOError:
            self._logger.critical(f'Error reading file.')
            raise SystemExit()

    def _set_valid_urls(self) -> None:
        for url in self._load_lines_from_file():
            if self.is_valid_youtube_url(url):
                self._urls.append(url)
            else:
                self._invalid_urls.append(url)

    def _assert_urls(self) -> None:
        if not self._urls:
            self._logger.critical('None of the urls are valid. Exiting...')
            raise SystemExit()

    def _assert_invalid_urls(self) -> None:
        if self._invalid_urls:
            urls = ', '.join(self._invalid_urls)
            self._logger.warning(f'Invalid urls: {urls}')
