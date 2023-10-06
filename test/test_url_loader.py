import os
import unittest
from ytracker.utils import load_urls, is_valid_youtube_url
from ytracker.exception import ProgramShouldExit


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
        if os.path.isfile('urls2.txt'):
            os.remove('urls2.txt')

    @staticmethod
    def prepare_file_with_zero_valid_urls():
        with open('urls2.txt', 'w') as file:
            file.write('http/woutubeWrongsome-channel\n'
                       'https://www.youtubeWhat-channel2\n'
                       'hs:/invalid_tube.com/@some-channel\n'
                       'random text\n')

    def test_is_valid_url(self):
        result = is_valid_youtube_url('https://www.youtube.com/@some-channel')
        self.assertTrue(result)
        self.assertFalse(not result)
        result2 = is_valid_youtube_url('https://www.youtubINVALID_URLme-channel')
        self.assertFalse(result2)
        self.assertTrue(not result2)

    def test_load_urls(self):
        result = load_urls('urls.txt')
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'https://www.youtube.com/@some-channel')
        self.assertEqual(result[1], 'https://www.youtube.com/@some-channel2')
        self.prepare_file_with_zero_valid_urls()
        self.assertRaises(ProgramShouldExit, load_urls, 'urls2.txt')


if __name__ == '__main__':
    unittest.main()
