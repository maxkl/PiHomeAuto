import threading
from collections import namedtuple
from datetime import datetime

from scheduler.sleeper import Sleeper


class Task(namedtuple('Task', ['hours', 'minutes', 'fn', 'args', 'kwargs'])):
    __slots__ = ()

    def __new__(cls, hours, minutes, fn, args=None, kwargs=None):
        self = super(Task, cls).__new__(cls, hours, minutes, fn, args if args is not None else (), kwargs if kwargs is not None else {})
        return self


class Scheduler:
    def __init__(self, query_tasks=lambda t: []):
        self._sleep = Sleeper()
        self._thread = None
        self._last_time = None
        self._query_tasks = query_tasks
        self._should_stop = False

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, name='Scheduler thread')
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        self._should_stop = True
        self._sleep.interrupt()

    def _run(self):
        while not self._should_stop:
            self._exec_tasks()
            if self._should_stop:
                break
            self._sleep.sleep(60 - datetime.now().second)

    def _exec_tasks(self):
        now = datetime.now()
        print('Executing tasks at {}'.format(now.strftime('%H:%M:%S')))

        time = (now.hour, now.minute)

        if time == self._last_time:
            return
        self._last_time = time

        tasks = self._query_tasks(time)
        for task in tasks:
            try:
                task.fn(*task.args, **task.kwargs)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                pass
