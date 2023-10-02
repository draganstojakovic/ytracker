import json
import os
from dataclasses import dataclass
from ytracker.logger import Logger


@dataclass(frozen=True, slots=True)
class CreateConfigStatus:
    success: bool
    exception: None | Exception = None
    msg: str | None = None


class Options:
    __slots__ = '_download_path', '_refresh_interval', '_storage_size', '_video_quality'

    def __init__(self, *, download_path=None, refresh_interval=None, storage_size=None, video_quality=None):
        self._download_path = download_path
        self._refresh_interval = refresh_interval
        self._storage_size = storage_size
        self._video_quality = video_quality

    @classmethod
    def create(
            cls,
            *,
            download_path=None,
            refresh_interval=None,
            storage_size=None,
            video_quality=None,
    ) -> 'Options':
        download_path: str = download_path if download_path is not None \
            else os.path.join(os.path.expanduser('~'), 'Videos', 'ytracker')

        refresh_interval: int = int(refresh_interval) if refresh_interval is not None else 120

        if isinstance(storage_size, int):
            storage_size: int = storage_size
        elif isinstance(storage_size, float):
            storage_size: int = int(storage_size)
        elif isinstance(storage_size, str):
            storage_size: int = int(float(storage_size))
        else:
            storage_size: int = 5

        video_quality: str = video_quality if video_quality in ('360', '480', '720', '1080') else '720'

        return cls(
            download_path=download_path,
            refresh_interval=refresh_interval,
            storage_size=storage_size,
            video_quality=video_quality
        )

    @property
    def download_path(self) -> str:
        return self._download_path

    @property
    def refresh_interval(self) -> int:
        return self._refresh_interval

    @property
    def storage_size(self) -> int:
        return self._storage_size

    @property
    def video_quality(self) -> str:
        return self._video_quality


class Config:
    __slots__ = '_options',

    def __init__(self, options: Options | None = None) -> None:
        self._options = options

    @property
    def options(self) -> Options:
        return self._options

    @options.setter
    def options(self, options: Options) -> None:
        self._options = options

    @classmethod
    def create(cls, logger: Logger) -> 'Config':
        config = cls()
        conf_path = config._conf_path()
        try:
            with open(conf_path, 'r') as config_file:
                config_data = json.load(config_file)
        except FileNotFoundError as e:
            logger.warning(f'File not found: {conf_path}, {e}')
        except PermissionError as e:
            logger.error(f'Insufficient permissions. Cannot read: {conf_path}, {e}')
        except json.JSONDecodeError as e:
            logger.error(f'Parsing failed: {conf_path}, {e}')
        else:
            config.options = Options.create(
                download_path=config_data.get('download_path'),
                refresh_interval=config_data.get('refresh_interval'),
                storage_size=config_data.get('storage_size'),
                video_quality=config_data.get('video_quality')
            )
        finally:
            if not isinstance(config.options, Options):
                config.options = Options.create()
                config_created = config._create_config_file(conf_path=conf_path)
                if not config_created.success:
                    logger.error(f'{config_created.msg}, {config_created.exception}')
                    # TODO toastify here
        return config

    @classmethod
    def _create_config_file(cls, conf_path: str, new_config=None) -> CreateConfigStatus:
        new_config = {
            'download_path': os.path.join(os.path.expanduser('~'), 'Videos', 'ytracker'),
            'refresh_interval': 2,
            'storage_size': 5,
            'video_quality': '720'
        } if new_config is None else new_config

        try:
            with open(conf_path, 'w') as config_file:
                json.dump(new_config, config_file, indent=2)
        except PermissionError as e:
            return CreateConfigStatus(False, e, f'Permission denied. Failed writing to: {conf_path}')
        except IOError as e:
            return CreateConfigStatus(False, e, f'Failed writing to: {conf_path}')
        else:
            return CreateConfigStatus(True)

    @staticmethod
    def _conf_path() -> str:
        config_path = os.path.join(
            os.path.expanduser('~'),
            '.config',
            'ytracker'
        )
        os.makedirs(config_path, exist_ok=True)

        return os.path.join(config_path, 'config.json')
