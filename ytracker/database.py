import os
import sqlite3
from typing import Optional, TypeAlias, Any
from abc import ABC, abstractmethod
from ytracker.global_constants import PACKAGE_NAME


class Criteria:
    __slots__ = '_where', '_order_by'

    def __init__(self):
        self._where = ''
        self._order_by = ''

    def __str__(self) -> str:
        if self._where == '' and self._order_by == '':
            return ''
        filter_query: str = self._where.strip()
        if filter_query.endswith('AND'):
            filter_query = filter_query[:-3]
        elif filter_query.endswith('OR'):
            filter_query = filter_query[:-2]
        order = self._order_by.strip()
        return f"{filter_query.strip()} {order}".strip()

    def where(self, statement: str, log_op='AND') -> 'Criteria':
        log_op: str = 'OR ' if log_op.upper() == 'OR' else f'{log_op} '
        where: str = '' if self._where.startswith('WHERE') else 'WHERE '
        self._where += f'{where}{statement} {log_op}'
        return self

    def order_by(self, column_name: str, order='') -> 'Criteria':
        order: str = 'DESC' if order.upper() == 'DESC' else ''
        if self._order_by.startswith('ORDER BY'):
            self._order_by = self._order_by.strip()
            self._order_by += f', {column_name} {order}'
        else:
            self._order_by += f'ORDER BY {column_name} {order}'
        return self


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
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
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
                    to_delete BOOLEAN NOT NULL DEFAULT 0,
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


COLUMN_NAME: TypeAlias = str
COLUMN_VALUE: TypeAlias = Any
CONSTRAINT: TypeAlias = tuple[COLUMN_NAME, COLUMN_VALUE]


class Table(ABC):
    __slots__ = 'database', 'table_name'

    def __init__(self, table_name: str):
        self.database = Database().file
        self.table_name = table_name

    @abstractmethod
    def _get(self, constraint: CONSTRAINT) -> 'Table':
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def delete(self) -> None:
        pass


class YouTubeVideo(Table):
    __slots__ = (
        'table_id',
        'video_id',
        'path_on_disk',
        'file_size',
        'to_delete',
        'deleted',
        'created_at',
        'updated_at'
    )

    def __init__(self, table_id: Optional[int] = None, video_id: Optional[str] = None):
        super().__init__('download_history')
        self.table_id: Optional[str] = None
        self.video_id: Optional[str] = None
        self.path_on_disk: Optional[str] = None
        self.file_size: Optional[int] = None
        self.to_delete: bool = False
        self.deleted: bool = False
        self.created_at = None
        self.updated_at = None

        if table_id is not None:
            self.table_id = table_id
            self._get(('id', table_id))
            return
        if video_id is not None:
            self._get(('youtube_video_id', video_id))

    @property
    def video(self) -> dict:
        return {
            'id': self.table_id,
            'youtube_video_id': self.video_id,
            'path_on_disk': self.path_on_disk,
            'file_size': self.file_size,
            'to_delete': bool(self.to_delete),
            'deleted': bool(self.deleted),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def set_table_id(self, table_id: int | str) -> 'YouTubeVideo':
        self.table_id = int(table_id)
        return self

    def set_youtube_video_id(self, video_id: str) -> 'YouTubeVideo':
        self.video_id = video_id
        return self

    def set_path_on_disk(self, path_on_disk: str) -> 'YouTubeVideo':
        self.path_on_disk = path_on_disk
        return self

    def set_file_size(self, file_size: int) -> 'YouTubeVideo':
        self.file_size = file_size
        return self

    def set_to_delete(self, to_delete: bool) -> 'YouTubeVideo':
        self.to_delete = to_delete
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

    def _get(self, constraint: CONSTRAINT) -> Optional['YouTubeVideo']:
        with sqlite3.connect(self.database) as conn:
            video = conn.cursor().execute(
                f"SELECT * FROM {self.table_name} WHERE {constraint[0]} = '{constraint[1]}'"
            ).fetchone()
            if video is None:
                return None
            self.table_id = video[0]
            self.video_id = video[1]
            self.path_on_disk = video[2]
            self.file_size = video[3]
            self.to_delete = video[4]
            self.deleted = video[5]
            self.created_at = video[6]
            self.updated_at = video[7]
            return self

    def save(self) -> bool:
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            insert_query: str = """
                INSERT INTO download_history
                (youtube_video_id, path_on_disk, file_size, to_delete, deleted)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                self.video_id,
                self.path_on_disk,
                self.file_size,
                self.to_delete,
                self.deleted
            ))
            conn.commit()

        return cursor.rowcount > 0

    def update(self) -> bool:
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            update_query: str = """
            UPDATE download_history
            SET
                youtube_video_id = ?,
                path_on_disk = ?,
                file_size = ?,
                to_delete = ?,
                deleted = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE
                id = ?
            """
            cursor.execute(update_query, (
                self.video_id,
                self.path_on_disk,
                self.file_size,
                self.to_delete,
                self.deleted,
                self.table_id
            ))
            conn.commit()

        return cursor.rowcount > 0

    def delete(self) -> bool:
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = '{self.table_id}'")
            conn.commit()

        return cursor.rowcount > 0


class Repository:
    def __init__(self, database: Database):
        self.database = database

    def matching(self, criteria: Optional[Criteria] = None) -> list['YouTubeVideo'] | list[None]:
        with sqlite3.connect(self.database.file) as conn:
            if criteria is None:
                query: str = """
                SELECT * FROM download_history
                """
                videos = conn.execute(query).fetchall()
                print(videos)
            else:
                pass

        return videos


if __name__ == '__main__':
    # print(YouTubeVideo()
    #       .set_youtube_video_id('kurac4')
    #       .set_path_on_disk('/somewhere-else')
    #       .set_file_size(2324)
    #       .save())
    repo = Repository(Database())
    repo.matching()
