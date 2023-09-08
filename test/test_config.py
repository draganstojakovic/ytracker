import os
import json
import unittest
import tempfile
import ytracker.config
from ytracker.constants import PACKAGE_NAME


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.path_to_config_file = self.config_path()
        self.config = ytracker.config.Config()

    @staticmethod
    def config_path() -> str:
        home = os.environ.get('HOME')
        config = os.path.join(home, '.config', PACKAGE_NAME)
        return os.path.join(config, 'config.json')

    def test_init_config(self):
        self.assertIsInstance(self.config, ytracker.config.Config)

    def test_generate_path_to_config_file(self):
        expected = self.path_to_config_file
        actual = self.config._config_file_path
        self.assertEqual(expected, actual)

    def test_config_options_property(self):
        self.assertIsInstance(self.config.options, ytracker.config._Options)

    def test_load_config_existing_valid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_config_file = os.path.join(temp_dir, 'config.json')
            with open(temp_config_file, 'w') as f:
                json.dump({
                    'download_path': '/temp/download',
                    'refresh_interval': 3,
                    'storage_size': 10,
                    'video_quality': '720'
                }, f)

            original_config_path = self.config._config_file_path
            self.config._config_file_path = temp_config_file

            self.config._load_config()
            self.assertEqual(self.config.options.download_path, '/temp/download')
            self.assertEqual(self.config.options.refresh_interval, 3)
            self.assertEqual(self.config.options.storage_size, 10)
            self.assertEqual(self.config.options.video_quality, '720')

            self.config._config_file_path = original_config_path

    def test_load_config_nonexistent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config._config_file_path = os.path.join(temp_dir, 'config.json')

            self.config._load_config()
            self.assertEqual(
                self.config.options.download_path,
                os.path.join(os.environ.get('HOME'), 'Videos', PACKAGE_NAME)
            )
            self.assertEqual(self.config.options.refresh_interval, 2)
            self.assertEqual(self.config.options.storage_size, 5)
            self.assertEqual(self.config.options.video_quality, '720')

    def test_load_config_existing_invalid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_config_file = os.path.join(temp_dir, 'config.json')
            with open(temp_config_file, 'w') as f:
                f.write("Invalid JSON data")

            original_config_path = self.config._config_file_path
            self.config._config_file_path = temp_config_file

            self.config._load_config()
            self.assertEqual(
                self.config.options.download_path,
                os.path.join(os.environ.get('HOME'), 'Videos', PACKAGE_NAME)
            )
            self.assertEqual(self.config.options.refresh_interval, 2)
            self.assertEqual(self.config.options.storage_size, 5)
            self.assertEqual(self.config.options.video_quality, '720')

            self.config._config_file_path = original_config_path


if __name__ == '__main__':
    unittest.main()
