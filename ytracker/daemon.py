import os
import signal
import sys
from typing import Literal
from ytracker.logger import Logger


class PidFileManager:
    __slots__ = '_file',

    def __init__(self, file_path=None) -> None:
        self._file = os.path.join(
            os.path.expanduser('~'),
            '.local',
            'share',
            'ytracker',
            'ytracker.pid'
        ) if file_path is None else file_path

    def read(self) -> int | bool:
        try:
            with open(self._file, 'r') as pid_file:
                pid_value = int(pid_file.read())
        except (PermissionError, FileNotFoundError, IOError):
            return False
        else:
            return pid_value

    def write(self, pid: int) -> bool:
        try:
            with open(self._file, 'w') as pid_file:
                pid_file.write(str(pid))
        except (PermissionError, IOError):
            return False
        else:
            return True


class Daemon:
    __slots__ = '_action', '_pid_manager', '_logger'

    def __init__(
            self,
            action: Literal['start', 'stop', 'restart'],
            /,
            pid_manager: PidFileManager,
            logger: Logger
    ) -> None:
        self._action = action
        self._pid_manager = pid_manager
        self._logger = logger

    def __enter__(self) -> None:
        return {
            'start': lambda: self._start(),
            'stop': lambda: self._stop(),
            'restart': lambda: self._restart(),
        }.get(self._action, None)()

    def __exit__(self):
        return True

    def _fork(self) -> None:
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            self._logger.critical(f'Subprocess forking failed, {e}')
            sys.exit(1)

    def _start(self) -> None:
        self._stop()
        self._logger.info('Starting a new daemon process...')
        self._fork()
        os.chdir('/')
        os.setsid()
        os.umask(0)
        self._fork()
        sys.stdout.flush()
        sys.stderr.flush()
        si = open('/dev/null', 'r')
        so = open('/dev/null', 'a+')
        se = open('/dev/null', 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        pid = os.getpid()
        if not self._pid_manager.write(pid):
            self._logger.critical(f'Failed writing pid "{pid}" to file. '
                                  f'Check if you have write permission.')
            self._kill(pid)
        else:
            self._logger.info(f'A new daemon process started: {pid}')

    def _stop(self) -> None:
        pid = self._pid_manager.read()
        if pid:
            self._kill(pid)

    def _restart(self) -> None:
        self._stop()
        self._start()

    def _kill(self, pid: int) -> None:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            if e.errno == 3:
                self._logger.warning(f'Program of pid "{pid}" is not running.')
