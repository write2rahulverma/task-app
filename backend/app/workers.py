import threading
import time
from queue import Queue, Empty
from typing import Callable, Any

class Job:
    def __init__(self, name: str, payload: Any):
        self.name = name
        self.payload = payload
        self.created_at = time.time()

class TaskWorker:
    def __init__(self, num_threads: int = 3):
        self._queue: Queue = Queue()
        self._threads: list[threading.Thread] = []
        self._handlers: dict[str, Callable] = {}
        self._running = False
        self._lock = threading.Lock()
        self.num_threads = num_threads
        self.processed_count = 0

    def register(self, job_name: str, handler: Callable) -> None:
        self._handlers[job_name] = handler

    def start(self) -> None:
        with self._lock:
            if self._running:
                return                
            self._running = True
            for i in range(self.num_threads):
                t = threading.Thread(
                    target=self._worker_loop,
                    name=f"Worker-{i}",
                    daemon=True,
                )
                t.start()
                self._threads.append(t)

    def _worker_loop(self) -> None:
        while self._running:
            try:
                job: Job = self._queue.get(timeout=1.0)
                self._execute(job)
                self._queue.task_done()
                with self._lock:
                    self.processed_count += 1
            except Empty:
                continue
            except Exception as e:
                print(f"[{threading.current_thread().name}] Error: {e}")

    def _execute(self, job: Job) -> None:
        handler = self._handlers.get(job.name)
        if handler:
            handler(job.payload)
        else:
            print(f"[Worker] No handler for job: {job.name}")

    def enqueue(self, job: Job) -> None:
        self._queue.put(job)

    def stop(self, wait: bool = True) -> None:
        if wait:
            self._queue.join()
        self._running = False

    def __repr__(self) -> str:
        return (f"TaskWorker(threads={self.num_threads}, "
                f"processed={self.processed_count},"
                f"queued={self._queue.qsize()}")
    
def _send_notification(payload: dict) -> None:
    print(f"[Notification] To {payload.get('email')} : {payload.get('message')}")
    time.sleep(0.05)

worker = TaskWorker(num_threads=3)
worker.register("notify", _send_notification)
worker.start()