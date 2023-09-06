import os
import re
from ytracker.constants import PACKAGE_NAME


class AllUrlsInvalidException(Exception):
    def __init__(self):
        super().__init__('All YouTube URLs are invalid.')


class UrlLoader:
    __slots__ = '_file_path', '_urls', '_invalid_urls'

    def __init__(self, file_path: str | None = None):
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
            # TODO LOG critical
            raise SystemExit()
        except IOError:
            # TODO LOG critical
            raise SystemExit()

    def _set_valid_urls(self) -> None:
        for url in self._load_lines_from_file():
            if self.is_valid_youtube_url(url):
                self._urls.append(url)
            else:
                self._invalid_urls.append(url)

    def _assert_urls(self) -> None:
        if not self._urls:
            raise AllUrlsInvalidException()

    def _assert_invalid_urls(self) -> None:
        # TODO LOG WARNING
        pass
