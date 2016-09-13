import threading

import sys


class Sleeper:
    def __init__(self):
        self._lock = threading.Lock()
        self._lock.acquire()
        self._sleeping = False

    def sleep(self, seconds):
        """
        Sleep the specified amount of seconds.
        Can be interrupted.

        :param float seconds: time to sleep

        :raises RuntimeError: if already sleeping in another process

        :return: True when slept for the specified time, False if interrupted
        """
        if self._sleeping:
            raise RuntimeError('Already sleeping')
        self._sleeping = True
        try:
            acquired = self._lock.acquire(timeout=seconds)
            return not acquired
        finally:
            # Make sure that the lock is really locked
            acquired = self._lock.acquire(blocking=False)
            if acquired:
                print('lock was not locked', file=sys.stderr)
            self._sleeping = False

    def interrupt(self):
        if self._sleeping:
            self._lock.release()
