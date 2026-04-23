import threading

from app.models.task import Task, TaskLog
from app.spider.crawler import SimpleCrawler


class TaskRunner:
    def __init__(self):
        self._lock = threading.Lock()
        self._threads = {}
        self._stop_events = {}

    def start(self, task_id):
        with self._lock:
            thread = self._threads.get(task_id)
            if thread and thread.is_alive():
                return False, '任务已在运行中'

            Task.clear_stop_request(task_id)
            stop_event = threading.Event()
            thread = threading.Thread(
                target=self._run_task,
                args=(task_id, stop_event),
                daemon=True,
                name=f'crawler-task-{task_id}',
            )
            self._stop_events[task_id] = stop_event
            self._threads[task_id] = thread
            thread.start()
            return True, '任务已启动'

    def stop(self, task_id, task):
        if task['status'] != 'running':
            return False, '当前任务未在运行中'

        Task.request_stop(task_id)
        TaskLog.create(task_id, '收到停止任务请求', 'warning')

        with self._lock:
            stop_event = self._stop_events.get(task_id)
            if stop_event:
                stop_event.set()

        return True, '已发送停止指令'

    def _run_task(self, task_id, stop_event):
        try:
            crawler = SimpleCrawler(task_id, stop_event=stop_event)
            crawler.run()
        finally:
            with self._lock:
                self._threads.pop(task_id, None)
                self._stop_events.pop(task_id, None)


task_runner = TaskRunner()
