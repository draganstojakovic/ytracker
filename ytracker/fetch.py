import os
from dataclasses import dataclass
from datetime import datetime
from ytracker.config import Config
from ytracker.database import YouTubeVideo
from ytracker.logger import Logger
from typing import Optional
from yt_dlp import YoutubeDL


class Urls:
    __slots__ = '_channel_urls', '_logger'

    def __init__(self, channel_urls: tuple, logger: Logger) -> None:
        self._channel_urls = channel_urls
        self._logger = logger

    def __iter__(self) -> str | None:
        for channel_url in self._channel_urls:
            for videos_info in self._get_info(channel_url):
                yield videos_info.get('url', None)

    # noinspection PyUnusedLocal
    @staticmethod
    def _is_downloaded(info, *, incomplete):
        video_id = info.get('id', False)
        if video_id and YouTubeVideo.exists(video_id):
            return 'Video is already downloaded.'

    def _get_info(self, playlist_url: str) -> Optional[list[dict]]:
        try:
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
                info = ydl.sanitize_info(
                    ydl.extract_info(playlist_url.strip(), download=False)
                ).get('entries')
        except Exception as e:
            self._logger.error(f'Error occurred while getting video info, {e}')
            return None
        else:
            return info


@dataclass(slots=True)
class VideoInfo:
    video_id: str
    path_on_disk: str
    file_size: int | None = None


class VideoFetcher:
    __slots__ = '_config', '_logger'

    def __init__(self, config: Config, logger: Logger) -> None:
        self._config = config
        self._logger = logger

    def _format_output_path(self, *, without_format: bool = False) -> str:
        download_path = self._config.options.download_path
        slash = '' if download_path.endswith('/') else '/'
        if without_format:
            return f'{download_path}{slash}'
        return f'{download_path}{slash}%(upload_date)s_%(uploader)s_%(id)s.%(ext)s'

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

    def _set_video_info(self, video_url: str) -> VideoInfo | bool:
        self._logger.info(f'Getting video info: {video_url}')
        with YoutubeDL({'quiet': True}) as ydl:
            video_info = ydl.sanitize_info(ydl.extract_info(video_url, download=False))

        if not isinstance(video_info, dict):
            self._logger.error('Video info not downloaded')
            return False

        download_path = self._format_output_path(without_format=True)

        uploader = video_info.get('uploader', False)
        if not uploader:
            return False
        video_id = video_info.get('id', False)
        if not video_id:
            return False
        upload_date = video_info.get('upload_date', datetime.now().strftime('%Y%m%d'))

        return VideoInfo(
            video_info.get('id', 'unknown-id'),
            f'{download_path}{upload_date}_{uploader}_{video_id}.mp4'
        )

    def download(self, video_url: str) -> VideoInfo | bool:
        video_info = self._set_video_info(video_url)
        if not video_info:
            return False
        self._logger.info(f'Started downloading: {video_url}')
        try:
            with YoutubeDL(
                    {
                        'quiet': True,
                        'outtmpl': self._format_output_path(),
                        'format': self._format_video_format()
                    }
            ) as ydl:
                ydl.download(video_url)
        except Exception as e:
            self._logger.error(f'YouTubeDL error occurred while downloading video, {e}')
            return False

        if not os.path.isfile(video_info.path_on_disk):
            self._logger.error(f'Video not downloaded: {video_info.path_on_disk}')
            return False

        self._logger.info(f'Finished downloading {video_url}')
        video_info.file_size = os.path.getsize(video_info.path_on_disk)

        return video_info
