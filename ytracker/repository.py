import os
import re
import sqlite3
from ytracker.global_constants import PACKAGE_NAME


class DatabaseFile:

    _instance = None

    _db_file: str | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseFile, cls).__new__(cls)
            cls._instance._create_database_file()
            cls._instance._setup_database()
        return cls._instance

    @staticmethod
    def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
        return connection.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        ).fetchone() is not None

    @property
    def db_file(self) -> str:
        if not os.path.exists(self._db_file):
            self._create_database_file()
            self._setup_database()
        return self._db_file

    def _create_database_file(self) -> None:
        home: str = os.environ.get('HOME')
        db_path: str = os.path.join(home, '.local', 'share', PACKAGE_NAME)
        os.makedirs(db_path, exist_ok=True)
        self._db_file: str = os.path.join(db_path, f'{PACKAGE_NAME}.db')

    def _setup_database(self) -> None:
        with sqlite3.connect(self._db_file) as conn:
            if not self._table_exists(conn, table_name='download_history'):
                create_table_query: str = """
                CREATE TABLE download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youtube_video_id TEXT,
                    path_on_disk TEXT,
                    file_size INTEGER,
                    deleted INTEGER DEFAULT 0,
                    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
                create_index_on_youtube_video_id: str = """
                CREATE INDEX idx_youtube_video_id ON download_history (youtube_video_id);
                """
                try:
                    conn.execute(create_table_query)
                    conn.execute(create_index_on_youtube_video_id)
                    conn.commit()
                except sqlite3.Error:
                    raise SystemExit()


class Criteria:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def condition(self) -> str:
        conditions = (f"{k} = '{v}'" for k, v in self.__dict__.items())
        return f"WHERE {' AND '.join(conditions)}"


class Repository:

    def __init__(self, database_file: DatabaseFile):
        self._db_file = database_file.db_file

    def exists(self, table_name: str, criteria: Criteria) -> bool:
        with sqlite3.connect(self._db_file) as conn:
            try:
                return conn.execute(
                    f"SELECT EXISTS (SELECT 1 FROM {table_name} {criteria.condition})"
                ).fetchone()[0] == 1
            except sqlite3.Error:
                raise SystemExit()


class InvalidYouTubeVideoIdException(Exception):
    pass


class MissingVideoException(Exception):
    def __init__(self, path: str):
        self.video_path = path
        super().__init__(f'Missing video: {path}')


class DatabaseModel:
    def __init__(self, table_name: str):
        self.table_name = table_name


class YouTubeVideo(DatabaseModel):

    _repository: Repository

    id: int

    yt_video_id: str

    path_on_disk: str

    file_size: int

    deleted: bool

    createdAt: str

    def __init__(
        self,
        video_path_on_disk: str | None,
        file_size: int | None,
        *,
        yt_video_id: str,
        repository: Repository
    ):
        self._repository = repository
        self._set_yt_video_id(yt_video_id)
        self._set_path_on_disk(video_path_on_disk)
        self._set_file_size(file_size)
        super().__init__('download_history')

    def _set_yt_video_id(self, yt_video_id: str) -> None:
        """
        Validates and sets YouTube video id
        :param yt_video_id:
        """
        pattern = re.compile(r'^[a-zA-Z0-9_-]{11}$')
        if not pattern.match(yt_video_id):
            raise InvalidYouTubeVideoIdException()
        self.yt_video_id = yt_video_id

    def _set_path_on_disk(self, path_on_disk: str) -> None:
        """
        Validates and sets path string to the file saved on disk.
        :param path_on_disk:
        """
        if not os.path.exists(path_on_disk):
            # This should be handled by removing the video entry for database
            raise MissingVideoException(path_on_disk)
        self.path_on_disk = path_on_disk

    def _set_file_size(self, file_size: int) -> None:
        """
        Sets the video file size defined in bytes
        :param file_size:
        """
        self.file_size = int(file_size)

    @property
    def youtube_video_data(self) -> dict:
        return {
            'id': self.id,
            'yt_video_id': self.yt_video_id,
            'path_on_disk': self.path_on_disk,
            'file_size': self.file_size,
            'deleted': self.deleted,
            'createdAt': self.createdAt
        }
