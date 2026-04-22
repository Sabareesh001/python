"""
Task queue broker and manager.
Handles task queuing, worker management, and result tracking.
"""

import threading
import uuid
from collections import deque
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from models import Task, TaskResult, TaskStatus, WorkerStats
from backend import ResultBackend, InMemoryBackend


class TaskQueue:
    """Thread-safe task queue with dead-letter support."""
    
    def __init__(self, queue_name: str = "default"):
        self.queue_name = queue_name
        self._queue: deque = deque()
        self._dead_letter_queue: deque = deque()
        self._lock = threading.RLock()
    
    def put(self, task: Task) -> None:
        """Add task to queue."""
        with self._lock:
            self._queue.append(task)
    
    def get(self, timeout: Optional[float] = None) -> Optional[Task]:
        """Get next task from queue."""
        with self._lock:
            if self._queue:
                return self._queue.popleft()
        return None
    
    def put_dead_letter(self, task: Task) -> None:
        """Move task to dead-letter queue."""
        with self._lock:
            self._dead_letter_queue.append(task)
    
    def get_dead_letters(self) -> List[Task]:
        """Get all dead-letter tasks."""
        with self._lock:
            return list(self._dead_letter_queue)
    
    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._queue)
    
    def dead_letter_size(self) -> int:
        """Get dead-letter queue size."""
        with self._lock:
            return len(self._dead_letter_queue)


class Broker:
    """Task broker managing queues, workers, and results."""
    
    def __init__(self, result_backend: Optional[ResultBackend] = None):
        self.queues: Dict[str, TaskQueue] = {}
        self._default_queue = TaskQueue("default")
        self.queues["default"] = self._default_queue
        
        self.result_backend = result_backend or InMemoryBackend()
        self.function_registry: Dict[str, Callable] = {}
        self.worker_stats: Dict[int, WorkerStats] = {}
        self.connected_workers: int = 0
        self._lock = threading.RLock()
    
    def register_function(self, func: Callable, name: Optional[str] = None) -> None:
        """Register a callable for task execution."""
        func_name = name or func.__name__
        self.function_registry[func_name] = func
    
    def enqueue(
        self,
        func_name: str,
        *args,
        task_id: Optional[str] = None,
        queue: str = "default",
        retry_limit: int = 3,
        **kwargs
    ) -> Task:
        """Enqueue a task for execution."""
        if func_name not in self.function_registry:
            raise ValueError(f"Function '{func_name}' not registered")
        
        task_id = task_id or str(uuid.uuid4())[:8]
        task = Task(
            task_id=task_id,
            func_name=func_name,
            args=args,
            kwargs=kwargs,
            retry_limit=retry_limit,
        )
        
        q = self.queues.get(queue, self._default_queue)
        q.put(task)
        
        print(f"Task queued: <Task id={task.task_id} func={func_name} status={TaskStatus.PENDING.value}>")
        
        return task
    
    def get_task(self, queue: str = "default") -> Optional[Task]:
        """Get next task from queue."""
        q = self.queues.get(queue, self._default_queue)
        return q.get()
    
    def register_worker(self, worker_id: int) -> None:
        """Register a worker process."""
        with self._lock:
            self.connected_workers += 1
            self.worker_stats[worker_id] = WorkerStats(worker_id)
            print(f"[BROKER] Worker {worker_id} connected ({self.connected_workers} total)")
    
    def unregister_worker(self, worker_id: int) -> None:
        """Unregister a worker process."""
        with self._lock:
            self.connected_workers -= 1
            print(f"[BROKER] Worker {worker_id} disconnected ({self.connected_workers} total)")
    
    def set_result(self, task_id: str, result: TaskResult) -> None:
        """Store task result."""
        self.result_backend.set(task_id, result)
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Retrieve task result."""
        return self.result_backend.get(task_id)
    
    def get_all_results(self) -> Dict[str, TaskResult]:
        """Get all stored results."""
        return self.result_backend.get_all()
    
    def move_to_dead_letter(self, task: Task, queue: str = "default") -> None:
        """Move task to dead-letter queue."""
        q = self.queues.get(queue, self._default_queue)
        q.put_dead_letter(task)
    
    def get_status(self, queue: str = "default") -> Dict[str, Any]:
        """Get queue status."""
        q = self.queues.get(queue, self._default_queue)
        return {
            'queue_name': queue,
            'pending_tasks': q.size(),
            'dead_letter_tasks': q.dead_letter_size(),
            'connected_workers': self.connected_workers,
        }
    
    def print_status(self) -> None:
        """Print broker status."""
        print("\n" + "=" * 70)
        print("[BROKER] Status")
        print("=" * 70)
        for queue_name, queue in self.queues.items():
            status = self.get_status(queue_name)
            print(f"Queue '{queue_name}':")
            print(f"  - Pending tasks: {status['pending_tasks']}")
            print(f"  - Dead-letter tasks: {status['dead_letter_tasks']}")
            print(f"  - Connected workers: {status['connected_workers']}")
