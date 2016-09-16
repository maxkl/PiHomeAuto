import threading
import sys
from datetime import datetime

from scheduler.sleeper import Sleeper


class Scheduler:
    def __init__(self, query_tasks, exec_task):
        self._sleep = Sleeper()
        self._thread = None
        self._last_time = None
        self._query_tasks = query_tasks
        self._exec_task = exec_task
        self._should_stop = False

    def start(self):
        # Only start if not already running
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
            # Wait until the next minute
            self._sleep.sleep(60 - datetime.now().second)

    def _exec_tasks(self):
        now = datetime.now()
        print('Executing tasks at {}'.format(now.strftime('%H:%M:%S')))

        time = now.hour * 60 + now.minute

        # Don't re-run tasks if they've just been executed
        if time == self._last_time:
            return
        self._last_time = time

        tasks = self._query_tasks(time)
        for task in tasks:
            # Ignore all exceptions except SIGINT and sys.exit()
            try:
                self._exec_task(task)
            except (KeyboardInterrupt, SystemExit):
                raise
            except () as e:
                print(str(e), file=sys.stderr)
