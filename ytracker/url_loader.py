import os
import re
from exception import ProgramShouldExit


class UrlLoader:
    __slots__ = '_urls',

    def __init__(self, urls: list[str]) -> None:
        self._urls = urls
        self.assert_urls()

    @classmethod
    def create(cls, package_name: str, file_path: str | None = None) -> 'UrlLoader':
        file_path = os.path.join(
            os.path.expanduser('~'),
            '.local',
            'share',
            package_name,
            f'{package_name}_urls.txt'
        ) if file_path is None else file_path

        try:
            with open(file_path, 'r') as file:
                lines = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            raise ProgramShouldExit(f'File not found: {file_path}', 1)
        except IOError:
            raise ProgramShouldExit(f'Failed reading from file: {file_path}', 1)

        return cls([url for url in lines if cls.is_valid_youtube_url(url)])

    @classmethod
    def is_valid_youtube_url(cls, url: str) -> bool:
        return re.match(r'https://www\.youtube\.com/@[^/]+', url) is not None

    @property
    def urls(self) -> str:
        for url in self._urls:
            yield url

    def assert_urls(self) -> None:
        if not self._urls:
            raise ProgramShouldExit('Zero valid YouTube urls.', 1)
