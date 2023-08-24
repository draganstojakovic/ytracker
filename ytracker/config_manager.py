import json
import os
from .global_constants import PACKAGE_NAME


class _Options:

    def __init__(self, /, download_path=None, split_by_channel=None, refresh_interval=None, storage_size=None):
        self._set_download_path(download_path)
        self._set_split_by_channel(split_by_channel)
        self._set_refresh_interval(refresh_interval)
        self._set_storage_size(storage_size)

    def _set_download_path(self, download_path: str | None) -> None:
        if download_path is not None:
            self.download_path = download_path
        else:
            home = os.environ.get('HOME')
            self.download_path = os.path.join(home, 'Videos', PACKAGE_NAME)

    def _set_split_by_channel(self, split_by_channel: bool | None) -> None:
        if split_by_channel is not None:
            self.split_by_channel = split_by_channel
        else:
            self.split_by_channel = False

    def _set_refresh_interval(self, refresh_interval: int | None) -> None:
        """

        :param refresh_interval: defines how often program will check for new content in hours
        """
        if refresh_interval is not None:
            self.refresh_interval = int(refresh_interval)
        else:
            self.refresh_interval = 2

    def _set_storage_size(self, storage_size: int | float | str | None) -> None:
        """

        :param storage_size: is maximum amount of gigabytes of storage videos can take
        """
        if storage_size is None:
            self.storage_size = 5
            return
        if storage_size is str:
            self.storage_size = int(float(storage_size))
            return
        self.storage_size = int(storage_size)


class Config:

    options: _Options

    _DEFAULT_CONFIG = {
        'download_path': os.path.join(os.environ.get('HOME'), 'Videos', PACKAGE_NAME),
        'split_by_channel': False,
        'refresh_interval': 2,
        'storage_size': 5
    }

    def __init__(self):
        self._generate_path_to_config_file()
        self._load_config()

    def _generate_path_to_config_file(self) -> None:
        home = os.environ.get('HOME')
        config_path = os.path.join(home, '.config', PACKAGE_NAME)
        os.makedirs(config_path, exist_ok=True)
        self._config_file_path = os.path.join(config_path, 'config.json')

    def _load_config(self) -> None:
        try:
            with open(self._config_file_path, 'r') as config_file:
                config_data = json.load(config_file)
                self.options = _Options(
                    download_path=config_data.get('download_path'),
                    split_by_channel=config_data.get('split_by_channel'),
                    refresh_interval=config_data.get('refresh_interval'),
                    storage_size=config_data.get('storage_size')
                )
        except FileNotFoundError:
            self._create_config_file()
            self.options = _Options()
        except json.JSONDecodeError:
            self._create_config_file()
            self.options = _Options()

    def _create_config_file(self) -> None:
        try:
            with open(self._config_file_path, 'w') as config_file:
                json.dump(self._DEFAULT_CONFIG, config_file, indent=2)
        except (PermissionError, FileNotFoundError, OSError):
            pass
