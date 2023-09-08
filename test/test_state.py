import unittest
from ytracker.state import YouTubeIDs


class TestState(unittest.TestCase):
    def test_instance(self):
        yt = YouTubeIDs()
        self.assertIsNotNone(yt)
        self.assertIsInstance(yt, YouTubeIDs)

    def test_state(self):
        yt = YouTubeIDs()
        yt.add('id1')
        self.assertEqual(yt.get, ['id1'])
        yt.add('id2').add('id3')
        self.assertEqual(yt.get, ['id1', 'id2', 'id3'])
        yt.add('id4').remove('id1')
        self.assertEqual(yt.get, ['id2', 'id3', 'id4'])
        yt.remove('id2').remove('id4')
        self.assertEqual(yt.get, ['id3'])
        yt.delete()
        self.assertEqual(yt.get, [])


if __name__ == '__main__':
    unittest.main()
