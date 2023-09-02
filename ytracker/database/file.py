import os
from ytracker.global_constants import PACKAGE_NAME


def database_file() -> str:
    db_root_path: str = os.path.join(
        os.environ.get('HOME'),
        '.local',
        'share',
        PACKAGE_NAME
    )
    os.makedirs(db_root_path, exist_ok=True)
    return os.path.join(db_root_path, 'ytracker.db')
