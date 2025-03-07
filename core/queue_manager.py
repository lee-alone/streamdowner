from queue import Queue
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DownloadTask:
    url: str
    save_path: str
    options: Dict[str, Any]
    priority: int = 0

class QueueManager:
    def __init__(self, max_concurrent=3):
        self.queue = Queue()
        self.active_tasks = set()
        self.max_concurrent = max_concurrent
    
    def add_task(self, task: DownloadTask):
        self.queue.put(task)
    
    def get_next_task(self) -> DownloadTask:
        if not self.queue.empty() and len(self.active_tasks) < self.max_concurrent:
            task = self.queue.get()
            self.active_tasks.add(task.url)
            return task
        return None
    
    def task_completed(self, url: str):
        if url in self.active_tasks:
            self.active_tasks.remove(url)
    
    def get_queue_size(self) -> int:
        return self.queue.qsize()
    
    def get_active_count(self) -> int:
        return len(self.active_tasks)