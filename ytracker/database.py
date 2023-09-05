import os
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from ytracker.constants import PACKAGE_NAME


class Database:
    __slots__ = '_file'

    def __init__(self):
        self._file: str = self._set_database_file()

    @staticmethod
    def _set_database_file() -> str:
        db_root_path: str = os.path.join(
            os.environ.get('HOME'),
            '.local',
            'share',
            PACKAGE_NAME
        )
        os.makedirs(db_root_path, exist_ok=True)
        return os.path.join(db_root_path, f'{PACKAGE_NAME}.db')

    @staticmethod
    def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
        return connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
            (table_name,)
        ).fetchone() is not None

    @property
    def file(self) -> str:
        with sqlite3.connect(self._file) as conn:
            if not self._table_exists(conn, 'download_history'):
                create_table_query: str = """
                CREATE TABLE download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youtube_video_id TEXT NOT NULL UNIQUE,
                    path_on_disk TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    deleted BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

        return self._file


@dataclass
class Constraint:
    column: str
    value: int | str | bool


class Table(ABC):
    __slots__ = 'database', 'table_name'

    def __init__(self, table_name: str):
        self.database = Database()
        self.table_name = table_name

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
    def _assert_required_values(self) -> bool:
        pass


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
        super().__init__('download_history')
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
                SELECT * FROM {instance.table_name}
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
                f'SELECT SUM(file_size) FROM {instance.table_name} WHERE deleted = 0'
            ).fetchone()[0]

    @classmethod
    def exists(cls, video_id: str) -> bool:
        instance = cls()
        with sqlite3.connect(instance.database.file) as conn:
            return conn.cursor().execute(
                f"SELECT COUNT(*) from {instance.table_name} WHERE youtube_video_id = '{video_id}'"
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

    def _assert_required_values(self) -> bool:
        return all(value is not None for value in (
            self.video_id,
            self.path_on_disk,
            self.file_size
        ))

    def _get(self, constraint: Constraint) -> Optional['YouTubeVideo']:
        with sqlite3.connect(self.database.file) as conn:
            video = conn.cursor().execute(
                f"SELECT * FROM {self.table_name} WHERE {constraint.column} = '{constraint.value}'"
            ).fetchone()
            if video is None:
                return None
            self.table_id, self.video_id, self.path_on_disk, self.file_size, \
                self.deleted, self.created_at, self.updated_at = video
            return self

    def save(self) -> bool:
        if not self._assert_required_values():
            raise ValueError('Cannot save video. Some or all required values are not set.')
        with sqlite3.connect(self.database.file) as conn:
            cursor = conn.cursor()
            insert_query: str = f"""
                INSERT INTO {self.table_name}
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
            UPDATE {self.table_name}
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
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = '{self.table_id}'")
            conn.commit()

        return cursor.rowcount > 0
