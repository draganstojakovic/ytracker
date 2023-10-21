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

import sys

from typing import Union, Generator

from ytracker.config import Config
from ytracker.daemon import Daemon, PidFileManager
from ytracker.database import YouTubeVideo
from ytracker.exception import ProgramShouldExit
from ytracker.utils import (
    Command,
    convert_gb_to_bytes,
    delete_file,
    ExitCode,
    handle_should_exit_exception,
    load_urls,
    parse_args,
    program_should_run,
    print_help,
    sleep
)
from ytracker.logger import Logger
from ytracker.fetch import Urls, VideoFetcher, VideoInfo


def download_video(logger: Logger, config: Config) -> Generator[Union[VideoInfo, bool], None, None]:
    try:
        urls = load_urls()
    except ProgramShouldExit as should_exit:
        handle_should_exit_exception(should_exit, logger)
    else:
        fetcher = VideoFetcher(config, logger)
        for video_url in Urls(urls, logger, config):
            yield fetcher.download(video_url)


def is_not_enough_space(logger: Logger, config: Config) -> bool:
    try:
        sum_file_size = YouTubeVideo.get_sum_file_size()
    except ProgramShouldExit as should_exit:
        handle_should_exit_exception(should_exit, logger)
    else:
        if sum_file_size is None:
            logger.error(f'Failed determining the summed file size of all videos.')
            # TODO: walk through folder and check each file
            return False

        return sum_file_size > convert_gb_to_bytes(config.options.storage_size)


def ytracker(argv: list, logger: Logger) -> int:
    command = parse_args(argv)

    if command.value == Command.HELP.value:
        return print_help()

    config = Config.create(logger)

    with Daemon(command.value, PidFileManager(), logger):
        if command == Command.STOP.value:
            return ExitCode.SUCCESS.value

        while program_should_run():
            for result in download_video(logger, config):
                if not isinstance(result, VideoInfo):
                    continue

                try:
                    new_video = YouTubeVideo() \
                        .set_youtube_video_id(result.video_id) \
                        .set_path_on_disk(result.path_on_disk) \
                        .set_file_size(result.file_size)
                    save_result = new_video.save()
                except ProgramShouldExit as should_exit:
                    handle_should_exit_exception(should_exit, logger)
                finally:
                    if not save_result:
                        logger.error(f'Failed saving video to database: {new_video.path_on_disk}')

            delete_attempts = 3

            while is_not_enough_space(logger, config):
                if delete_attempts == 0:
                    logger.error('Failed deleting a video too many times.')
                    break
                try:
                    video = YouTubeVideo.get_oldest_not_deleted_video().set_deleted(True)
                    video.update()
                except ProgramShouldExit as should_exit:
                    handle_should_exit_exception(should_exit, logger)
                except Exception as e:
                    delete_attempts -= 1
                    logger.error(f'Unexpected exception: {e}')
                    continue
                else:
                    delete_file(video.path_on_disk, logger)

            sleep(logger, config.options.refresh_interval)


def main():
    default_logger = Logger()
    try:
        sys.exit(ytracker(sys.argv, default_logger))
    except Exception as e:
        default_logger.critical(str(e))
        sys.exit(ExitCode.FAILURE.value)


if __name__ == '__main__':
    main()
