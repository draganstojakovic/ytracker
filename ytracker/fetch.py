import os
import json
from config import Config
from datetime import datetime
from ytracker.database import YouTubeVideo
from ytracker.logger import Logger
from typing import Optional
from yt_dlp import YoutubeDL


class VideoInfo:
    __slots__ = '_channel_urls', '_logger'

    def __init__(self, channel_urls: list[str], logger: Logger) -> None:
        if not channel_urls:
            raise ValueError('Channel list cannot be empty')
        self._channel_urls = channel_urls
        self._logger = logger

    # noinspection PyUnusedLocal
    @staticmethod
    def _is_downloaded(info, *, incomplete):
        video_id = info.get('id', False)
        if video_id and YouTubeVideo.exists(video_id):
            return 'Video is already downloaded.'

    def _get_info(self, playlist_url: str) -> Optional[list[dict]]:
        with YoutubeDL(
                {
                    'match_filter': self._is_downloaded,
                    'lazy_playlist': True,
                    'break_per_url': True,
                    'playlistend': 10,
                    'extract_flat': True,
                    'quiet': True,
                }
        ) as ydl:
            self._logger.info(f'Getting videos from playlist: {playlist_url}')
            return ydl.sanitize_info(
                ydl.extract_info(playlist_url.strip(), download=False)
            ).get('entries')

    def channel_urls(self) -> Optional[tuple]:
        for url in self._channel_urls:
            yield tuple(video_info.get('url', None) for video_info in self._get_info(url))


class VideoFetcher:
    __slots__ = '_config', '_logger'

    def __init__(self, config: Config, logger: Logger) -> None:
        self._config = config
        self._logger = logger

    def _format_output_path(self, /, without_format: bool = False) -> str:
        download_path = self._config.options.download_path
        slash = '' if download_path.endswith('/') else '/'
        if without_format:
            return f'{download_path}{slash}'
        return f'{download_path}{slash}%(upload_date)s_%(uploader)s:%(title)s.%(ext)s'

    def _format_video_format(self) -> str:
        video_format = self._config.options.video_quality
        if video_format == '1080':
            return '137'
        if video_format == '720':
            return '22'
        if video_format == '480':
            return '135'
        if video_format == '360':
            return '18'

    def _set_video_info(self, video_url: str) -> dict | bool:
        self._logger.info(f'Getting video info: {video_url}')
        with YoutubeDL({'quiet': True}) as ydl:
            video_info = ydl.sanitize_info(
                ydl.extract_info(video_url, download=False)
            )

        if not isinstance(video_info, dict):
            self._logger.error('Video info not downloaded')
            return False

        download_path = self._format_output_path(without_format=True)

        uploader = video_info.get('uploader')
        if not uploader:
            return False
        title = video_info.get('title')
        if not title:
            return False
        upload_date = video_info.get('upload_date', datetime.now().strftime('%Y%m%d'))

        video_info = {
            'video_id': video_info.get('id', 'unknown-id'),
            'path_on_disk': f"{download_path}{upload_date}_{uploader}:{title}.mp4",
            'file_size': None
        }

        self._logger.info(f'Finished getting video info: {json.dumps(video_info)}')

        return video_info

    def download(self, video_url: str) -> dict | bool:
        video_info = self._set_video_info(video_url)
        if not video_info:
            return False
        self._logger.info(f'Started downloading: {video_url}')
        with YoutubeDL(
                {
                    'quiet': True,
                    'outtmpl': self._format_output_path(),
                    'format': self._format_video_format()
                }
        ) as ydl:
            ydl.download(video_url)

        path_to_vid = video_info.get('path_on_disk')
        if not os.path.isfile(path_to_vid):
            self._logger.error(f'Video not downloaded: {path_to_vid}')
            return False

        self._logger.info(f'Finished downloading {video_url}')
        video_info['file_size'] = os.path.getsize(path_to_vid)
        self._logger.info(f'Updated file_size: {video_info}')

        return video_info
