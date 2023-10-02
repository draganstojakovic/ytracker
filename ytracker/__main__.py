"""
MIT License

Copyright (c) 2023 Dragan Stojakovic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
import sys

from enum import Enum
from typing import Union, Generator

from ytracker.config import Config
from ytracker.daemon import Daemon, PidFileManager
from ytracker.database import YouTubeVideo
from ytracker.exception import ProgramShouldExit
from ytracker.utils import (
    Command,
    convert_gb_to_bytes,
    delete_file,
    load_urls,
    parse_args,
    program_should_run,
    print_help
)
from ytracker.logger import Logger
from ytracker.fetch import Urls, VideoFetcher, VideoInfo


logger = Logger()
config = Config.create(logger)


class ExitCode(Enum):
    SUCCESS = 0
    FAILURE = 1


def handle_save_video_data(video_data: VideoInfo) -> bool:
    try:
        saved_video = YouTubeVideo().set_youtube_video_id(
            video_id=video_data.video_id
        ).set_path_on_disk(
            path_on_disk=video_data.path_on_disk
        ).set_file_size(
            file_size=video_data.file_size
        ).save()
    except ProgramShouldExit as should_exit:
        logger.critical(should_exit.msg)
        sys.exit(should_exit.code)
    else:
        return saved_video


def handle_download_video() -> Generator[Union[VideoInfo, bool], None, None]:
    try:
        urls = load_urls()
    except ProgramShouldExit as should_exit:
        logger.critical(should_exit.msg)
        sys.exit(should_exit.code)
    else:
        for video_url in Urls(urls, logger):
            yield VideoFetcher(config, logger).download(video_url)


def is_not_enough_space() -> bool:
    sum_file_size = YouTubeVideo.get_sum_file_size()
    try:
        return sum_file_size > convert_gb_to_bytes(config.options.storage_size)
    except ProgramShouldExit as should_exit:
        logger.critical(should_exit.msg)
        sys.exit(should_exit.code)


def main(argv: list) -> int:
    command = parse_args(argv)

    if command.value == Command.HELP.value:
        return print_help()

    with Daemon(command.value, PidFileManager(), logger):
        if command == Command.STOP.value:
            return ExitCode.SUCCESS.value

        while program_should_run():
            for result in handle_download_video():
                if isinstance(result, VideoInfo):
                    handle_save_video_data(result)

            while is_not_enough_space():
                video = YouTubeVideo.get_latest_not_deleted_video().set_deleted(True)
                video.update()
                delete_file(video.path_on_disk, logger)

            time.sleep(config.options.refresh_interval * 60)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except Exception as e:
        logger.critical(str(e))
        sys.exit(ExitCode.FAILURE.value)
