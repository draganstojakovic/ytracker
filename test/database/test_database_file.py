import os
import unittest
from ytracker.database.file import database_file
from ytracker.global_constants import PACKAGE_NAME


class TestDatabaseFile(unittest.TestCase):

    @classmethod
    def setUp(cls) -> None:
        cls.expected_db_file_location = os.path.join(
            os.environ.get('HOME'),
            '.local',
            'share',
            PACKAGE_NAME,
            f'{PACKAGE_NAME}.db'
        )

    def test_database_file(self):
        actual_db_file = database_file()
        self.assertEqual(self.expected_db_file_location, actual_db_file)
        self.assertNotEqual('/wrong/database/file/location', actual_db_file)
        self.assertNotEqual('', actual_db_file)
        self.assertIsNotNone(self.expected_db_file_location, actual_db_file)


if __name__ == '__main__':
    unittest.main()
