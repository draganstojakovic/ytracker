import os
import time
import unittest
from ytracker.database import Constraint, Database, DBPath, YouTubeVideo


class TestDatabase(unittest.TestCase):
    def setUp(self):
        db_path = self.get_db_path()
        if os.path.isfile(db_path):
            os.remove(db_path)

    @classmethod
    def tearDownClass(cls) -> None:
        db_path = cls.get_db_path()
        if os.path.isfile(db_path):
            os.remove(db_path)

    @staticmethod
    def get_db_path() -> str:
        return os.path.join(
            os.environ.get('HOME'),
            '.local',
            'share',
            'ytracker',
            'ytracker.db'
        )

    @staticmethod
    def add_videos() -> None:
        (YouTubeVideo().set_youtube_video_id('id1')
         .set_path_on_disk('/videos/video.mp4').set_file_size(142234).save())
        # Need to pause between inserts so that created_at value is not identical for each entry
        time.sleep(1)
        (YouTubeVideo().set_youtube_video_id('id2')
         .set_path_on_disk('/videos/video.mp4').set_file_size(142234).save())
        time.sleep(1)
        (YouTubeVideo().set_youtube_video_id('id3')
         .set_path_on_disk('/videos/video.mp4').set_file_size(142234)
         .set_deleted(True).save())

    def test_constraint(self):
        constraint = Constraint('id', 1)
        self.assertIsNotNone(constraint)
        self.assertIsInstance(constraint, Constraint)
        self.assertEqual(constraint.column, 'id')
        self.assertEqual(constraint.value, 1)

    def test_DBPath(self):
        db_path = DBPath('/path/to/', 'database.db')
        self.assertIsInstance(db_path, DBPath)
        self.assertEqual(db_path.dir, '/path/to/')
        self.assertEqual(db_path.file, 'database.db')
        self.assertEqual(db_path.full_path, '/path/to/database.db')

    def test_database(self):
        db = Database.create('ytracker', 'database.db')
        self.assertIsInstance(db, Database)
        self.assertEqual(db.file, os.path.join(os.path.expanduser('~'), 'database.db'))
        self.add_videos()
        yt = YouTubeVideo(1)
        self.assertIsNotNone(yt)
        self.assertIsInstance(yt, YouTubeVideo)
        self.assertEqual(yt.video['youtube_video_id'], 'id1')
        self.assertEqual(yt.video['path_on_disk'], '/videos/video.mp4')
        self.assertEqual(yt.video['file_size'], 142234)
        self.assertEqual(yt.video['deleted'], False)
        video = YouTubeVideo.find_by_video_id('id3')
        self.assertIsNotNone(video)
        self.assertEqual(video.video['youtube_video_id'], 'id3')
        self.assertEqual(video.video['deleted'], True)
        last_not_deleted_video = YouTubeVideo.get_oldest_not_deleted_video()
        self.assertIsNotNone(last_not_deleted_video)
        self.assertEqual(last_not_deleted_video.video['youtube_video_id'], 'id2')
        file_size_sum = YouTubeVideo.get_sum_file_size()
        self.assertEqual(file_size_sum, 284468)
        exists = YouTubeVideo.exists('id1')
        self.assertTrue(exists)
        not_exists = YouTubeVideo.exists('id13243')
        self.assertFalse(not_exists)
        new_video = YouTubeVideo().set_youtube_video_id('id4').set_path_on_disk('/some_path').set_file_size(1).save()
        self.assertIsNotNone(new_video)
        self.assertTrue(new_video)
        self.assertTrue(YouTubeVideo.exists('id4'))
        self.assertTrue(YouTubeVideo.find_by_video_id('id4').set_deleted(True).update())
        self.assertTrue(YouTubeVideo.exists('id4'))
        self.assertTrue(YouTubeVideo.find_by_video_id('id4').delete())
        # TODO add more cases


if __name__ == '__main__':
    unittest.main()
