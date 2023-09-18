import os
import sqlite3
from abc import ABC, abstractmethod
from constants import PACKAGE_NAME
from dataclasses import dataclass
from exception import ProgramShouldExit
from typing import Optional, Callable


@dataclass(frozen=True, slots=True)
class DBPath:
    dir: str
    file: str

    @property
    def full_path(self) -> str:
        return os.path.join(self.dir, self.file)


@dataclass(frozen=True, slots=True)
class Constraint:
    column: str
    value: int | str | bool


class Database:
    __slots__ = '_file',

    def __init__(self, db_file_path: str) -> None:
        self._file = db_file_path

    @property
    def file(self) -> str:
        return self._file

    @classmethod
    def create(cls, package_name: str, db_file_path: str | None = None) -> 'Database':
        db = cls.default_db_path(package_name) if db_file_path is None \
            else cls.parse_db_path(db_file_path)
        os.makedirs(db.dir, exist_ok=True)

        return cls(db.full_path)

    @staticmethod
    def parse_db_path(path: str) -> DBPath:
        try:
            last_slash_index = path.rindex('/')
        except ValueError:
            last_slash_index = None

        get_file_path: Callable[[str], str] = lambda file_path: file_path \
            if any(ext in path for ext in ('.db', 'db3', 'sqlite', '.sqlite3')) else f'{file_path}.db'

        if last_slash_index is not None:
            db_path = path[0:last_slash_index]
            db_file = get_file_path(path[last_slash_index+1:])
        else:
            db_path = os.path.expanduser('~')
            db_file = get_file_path(path)

        return DBPath(dir=db_path, file=db_file)

    @staticmethod
    def default_db_path(package_name: str) -> DBPath:
        db_dir = os.path.join(
            os.path.expanduser('~'),
            '.local',
            'share',
            package_name
        )
        return DBPath(dir=db_dir, file=f'{package_name}.db')


class Table(ABC):
    __slots__ = '_database', '_table_name'

    def __init__(self, table_name: str, database: Database):
        self._table_name = table_name.strip()
        self._database = database
        if not self._validate_table():
            if not self._create_table():
                raise ProgramShouldExit('Failed creating database.', 1)

    @abstractmethod
    def _get(self, constraint: Constraint) -> 'Table':
        pass

    @abstractmethod
    def save(self) -> bool:
        pass

    @abstractmethod
    def update(self) -> bool:
        pass

    @abstractmethod
    def delete(self) -> bool:
        pass

    @abstractmethod
    def _assert_required(self) -> bool:
        pass

    @abstractmethod
    def _validate_table(self) -> bool:
        pass

    @abstractmethod
    def _create_table(self) -> bool:
        pass

    @property
    def table(self) -> str:
        return self._table_name

    @property
    def database(self) -> Database:
        return self._database


class YouTubeVideo(Table):
    __slots__ = (
        'table_id',
        'video_id',
        'path_on_disk',
        'file_size',
        'deleted',
        'created_at',
        'updated_at'
    )

    def __init__(self, table_id: Optional[int] = None, /):
        super().__init__('download_history', Database.create(PACKAGE_NAME))
        self.table_id: Optional[int] = None
        self.video_id: Optional[str] = None
        self.path_on_disk: Optional[str] = None
        self.file_size: Optional[int] = None
        self.deleted: bool = False
        self.created_at: Optional[str] = None
        self.updated_at: Optional[str] = None

        if table_id is not None:
            self.table_id = table_id
            self._get(Constraint('id', table_id))

    @classmethod
    def find_by_video_id(cls, video_id: str) -> Optional['YouTubeVideo']:
        return cls()._get(Constraint('youtube_video_id', video_id))

    @classmethod
    def get_latest_not_deleted_video(cls) -> Optional['YouTubeVideo']:
        instance = cls()
        with sqlite3.connect(instance.database.file) as conn:
            query: str = f"""
                SELECT * FROM {instance.table}
                WHERE deleted = 0
                ORDER BY created_at DESC
                LIMIT 1
            """
            video = conn.cursor().execute(query).fetchone()
            if video is None:
                return None
            instance.table_id, instance.video_id, instance.path_on_disk, instance.file_size, \
                instance.deleted, instance.created_at, instance.updated_at = video
            return instance

    @classmethod
    def get_sum_file_size(cls) -> Optional[int]:
        instance = cls()
        with sqlite3.connect(instance.database.file) as conn:
            return conn.cursor().execute(
                f'SELECT SUM(file_size) FROM {instance.table} WHERE deleted = 0'
            ).fetchone()[0]

    @classmethod
    def exists(cls, video_id: str) -> bool:
        instance = cls()
        with sqlite3.connect(instance.database.file) as conn:
            return conn.cursor().execute(
                f"SELECT COUNT(*) from {instance.table} WHERE youtube_video_id = '{video_id}'"
            ).fetchone()[0] > 0

    @property
    def video(self) -> dict:
        return {
            'id': self.table_id,
            'youtube_video_id': self.video_id,
            'path_on_disk': self.path_on_disk,
            'file_size': self.file_size,
            'deleted': bool(self.deleted),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def set_youtube_video_id(self, video_id: str) -> 'YouTubeVideo':
        self.video_id = video_id
        return self

    def set_path_on_disk(self, path_on_disk: str) -> 'YouTubeVideo':
        self.path_on_disk = path_on_disk
        return self

    def set_file_size(self, file_size: int) -> 'YouTubeVideo':
        self.file_size = file_size
        return self

    def set_deleted(self, deleted: bool) -> 'YouTubeVideo':
        self.deleted = deleted
        return self

    def set_created_at(self, created_at: str) -> 'YouTubeVideo':
        self.created_at = created_at
        return self

    def set_updated_at(self, updated_at: str) -> 'YouTubeVideo':
        self.updated_at = updated_at
        return self

    def _assert_required(self) -> bool:
        return all(value is not None for value in (
            self.video_id,
            self.path_on_disk,
            self.file_size
        ))

    def _validate_table(self) -> bool:
        with sqlite3.connect(self.database.file) as conn:
            return conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
                (self.table,)
            ).fetchone() is not None

    def _create_table(self) -> bool:
        create_table_query = f"""
        CREATE TABLE {self.table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            youtube_video_id TEXT NOT NULL UNIQUE,
            path_on_disk TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        create_index_on_youtube_video_id = """
        CREATE INDEX idx_youtube_video_id ON download_history (youtube_video_id);
        """
        with sqlite3.connect(self.database.file) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            cursor.execute(create_index_on_youtube_video_id)
            conn.commit()

        return self._validate_table()

    def _get(self, constraint: Constraint) -> Optional['YouTubeVideo']:
        with sqlite3.connect(self.database.file) as conn:
            video = conn.cursor().execute(
                f"SELECT * FROM {self.table} WHERE {constraint.column} = '{constraint.value}'"
            ).fetchone()
            if video is None:
                return None
            self.table_id, self.video_id, self.path_on_disk, self.file_size, \
                self.deleted, self.created_at, self.updated_at = video
            return self

    def save(self) -> bool:
        if not self._assert_required():
            raise ValueError('Cannot save video. Some or all required values are not set.')
        with sqlite3.connect(self.database.file) as conn:
            cursor = conn.cursor()
            insert_query: str = f"""
                INSERT INTO {self.table}
                (youtube_video_id, path_on_disk, file_size, deleted)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                self.video_id,
                self.path_on_disk,
                self.file_size,
                self.deleted
            ))
            conn.commit()

        return cursor.rowcount > 0

    def update(self) -> bool:
        with sqlite3.connect(self.database.file) as conn:
            cursor = conn.cursor()
            update_query: str = f"""
            UPDATE {self.table}
            SET
                youtube_video_id = ?,
                path_on_disk = ?,
                file_size = ?,
                deleted = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE
                id = ?
            """
            cursor.execute(update_query, (
                self.video_id,
                self.path_on_disk,
                self.file_size,
                self.deleted,
                self.table_id
            ))
            conn.commit()

        return cursor.rowcount > 0

    def delete(self) -> bool:
        with sqlite3.connect(self.database.file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table} WHERE id = '{self.table_id}'")
            conn.commit()

        return cursor.rowcount > 0
