import os
import unittest
from ytracker.url_loader import UrlLoader


class TestUrlLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open('urls.txt', 'w') as file:
            file.write('https://www.youtube.com/@some-channel\n'
                       'https://www.youtube.com/@some-channel2\n'
                       'https:/invalid_tube.com/@some-channel\n'
                       'random text\n')

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isfile('urls.txt'):
            os.remove('urls.txt')

    def test_url_loader_is_valid_url(self):
        self.assertTrue(UrlLoader.is_valid_youtube_url('https://www.youtube.com/@some-channel'))
        self.assertFalse(UrlLoader.is_valid_youtube_url('not a valid url'))

    def test_url_loader(self):
        self.assertTrue(os.path.isfile('urls.txt'))
        url_loader = UrlLoader('urls.txt')
        self.assertIsNotNone(url_loader)
        self.assertIsInstance(url_loader, UrlLoader)
        self.assertEqual(
            url_loader.urls,
            ['https://www.youtube.com/@some-channel', 'https://www.youtube.com/@some-channel2']
        )
        self.assertEqual(
            url_loader._invalid_urls,
            ['https:/invalid_tube.com/@some-channel', 'random text']
        )
        os.remove('urls.txt')
        with self.assertRaises(SystemExit):
            UrlLoader('urls.txt')
        # TODO add more cases


if __name__ == '__main__':
    unittest.main()
