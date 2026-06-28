import time
import threading
from app.workers import TaskWorker, Job

class TestTaskWorker:
    def setup_method(self):
        self.results = []
        self.lock = threading.Lock()

    def _collector(self, payload):
        with self.lock:
            self.results.append(payload)
    
    def test_worker_processes_jobs(self):
        w = TaskWorker(num_threads=2)
        w.register("collect", self._collector)
        w.start()
        for i in range (5):
            w.enqueue(Job("collect", {"n": i}))
        w.stop(wait=True)
        assert len(self.results) == 5

    def test_worker_parallel_execution(self):
        times = []
        lock = threading.Lock()

        def slow_job(payload):
            time.sleep(0.05)
            with lock:
                times.append(time.time())

        w = TaskWorker(num_threads=4)
        w.register("slow", slow_job)
        w.start()
        start = time.time()
        for _ in range(4):
            w.enqueue(Job("slow", {}))
        w.stop(wait=True)
        elapsed = time.time() - start
        assert elapsed < 0.15, f"Expected parallel execution, got {elapsed:.2f}s"

    def test_unknown_job_does_not_crash(self):
        w = TaskWorker(num_threads=1)
        w.start()
        w.enqueue(Job("nonexistent_handler", {}))
        w.stop(wait=True)

    def test_processed_count_increments(self):
        w = TaskWorker(num_threads=2)
        w.register("noop", lambda p: None)
        w.start()
        for _ in range(10):
            w.enqueue(Job("noop", {}))
        w.stop(wait=True)
        assert w.processed_count == 10