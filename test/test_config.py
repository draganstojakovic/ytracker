import os
import unittest
from ytracker.config import Options, Config
from ytracker.logger import Logger


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.home = os.path.expanduser('~')

    def test_options(self):
        options = Options.create(
            download_path='/some-path',
            refresh_interval=2,
            storage_size=10,
            video_quality='720'
        )

        self.assertIsNotNone(options)
        self.assertIsInstance(options, Options)

        self.assertEqual(options.download_path, '/some-path')
        self.assertEqual(options.refresh_interval, 2)
        self.assertEqual(options.storage_size, 10)
        self.assertEqual(options.video_quality, '720')

        self.assertNotEqual(options.download_path, '/some-wrong-path')
        self.assertNotEqual(options.refresh_interval, 3)
        self.assertNotEqual(options.storage_size, 5)
        self.assertNotEqual(options.video_quality, '1000')

        options = Options.create()

        self.assertIsNotNone(options)
        self.assertIsInstance(options, Options)

        self.assertEqual(options.download_path, f'{self.home}/Videos/ytracker')
        self.assertEqual(options.storage_size, 5)
        self.assertEqual(options.video_quality, '720')
        self.assertEqual(options.refresh_interval, 120)

    def test_config(self):
        conf = Config.create(Logger())

        self.assertIsNotNone(conf)
        self.assertIsInstance(conf, Config)
        self.assertIsNotNone(conf.options)
        self.assertIsInstance(conf.options, Options)

        self.assertEqual(conf.options.video_quality, '720')
        self.assertEqual(conf.options.storage_size, 5)
        self.assertEqual(conf.options.refresh_interval, 2)
        self.assertEqual(conf.options.download_path, f'{self.home}/Videos/ytracker')

        conf.options = Options.create(
            download_path='/some-path',
            refresh_interval=2,
            storage_size=10,
            video_quality='720'
        )

        self.assertEqual(conf.options.download_path, '/some-path')
        self.assertEqual(conf.options.refresh_interval, 2)
        self.assertEqual(conf.options.storage_size, 10)
        self.assertEqual(conf.options.video_quality, '720')


if __name__ == '__main__':
    unittest.main()
