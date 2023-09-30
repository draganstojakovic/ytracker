import os
import re
from enum import Enum
from ytracker.exception import ProgramShouldExit


def is_valid_youtube_url(url: str) -> bool:
    return re.match(r'https://www\.youtube\.com/@[^/]+', url) is not None


def load_urls(file_path=None) -> tuple:
    file_path = os.path.join(
        os.path.expanduser('~'),
        '.local',
        'share',
        'ytracker',
        'ytracker_urls.txt'
    ) if file_path is None else file_path

    try:
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        raise ProgramShouldExit(f'File not found: {file_path}', 1)
    except IOError:
        raise ProgramShouldExit(f'Failed reading from file: {file_path}', 1)

    urls = tuple(url for url in lines if is_valid_youtube_url(url))

    if not urls:
        raise ProgramShouldExit('Zero valid YouTube urls.', 1)

    return urls


class Command(Enum):
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'
    HELP = 'help'


def parse_args(args: list[str]) -> Command:
    if len(args) == 1:
        return Command.HELP

    arg = args[1]

    if arg == 'start':
        return Command.START
    if arg == 'stop':
        return Command.STOP
    if arg == 'restart':
        return Command.RESTART
    if arg == 'help':
        return Command.HELP

    return Command.HELP
