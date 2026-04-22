"""
Worker process for task execution with retry logic.
Implements exponential backoff for failed tasks.
"""

import time
import multiprocessing
from typing import Optional
from datetime import datetime
from models import Task, TaskResult, TaskStatus


class ExponentialBackoff:
    """Implements exponential backoff algorithm."""
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def get_delay(self, retry_count: int) -> float:
        """Calculate delay for given retry count."""
        delay = self.base_delay * (2 ** retry_count)
        return min(delay, self.max_delay)


class Worker:
    """Worker process for executing queued tasks."""
    
    def __init__(self, worker_id: int, broker, poll_interval: float = 1.0):
        self.worker_id = worker_id
        self.broker = broker
        self.poll_interval = poll_interval
        self.backoff = ExponentialBackoff()
        self.running = True
    
    def run(self) -> None:
        """Main worker loop."""
        self.broker.register_worker(self.worker_id)
        
        try:
            print(f"[WORKER-{self.worker_id}] Started")
            
            while self.running:
                # Get task from queue
                task = self.broker.get_task()
                
                if task is None:
                    time.sleep(self.poll_interval)
                    continue
                
                # Execute task
                result = self._execute_task(task)
                
                # Store result
                self.broker.set_result(task.task_id, result)
                
                # Update worker stats
                if result.status == TaskStatus.SUCCESS:
                    self.broker.worker_stats[self.worker_id].successful_tasks += 1
                    self.broker.worker_stats[self.worker_id].total_time += result.duration or 0
                else:
                    self.broker.worker_stats[self.worker_id].failed_tasks += 1
                
                self.broker.worker_stats[self.worker_id].total_tasks += 1
        
        finally:
            self.broker.unregister_worker(self.worker_id)
    
    def _execute_task(self, task: Task) -> TaskResult:
        """Execute a single task with retry logic."""
        result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
        )
        
        retry_count = 0
        last_error = None
        
        while retry_count <= task.retry_limit:
            try:
                result.started_at = datetime.now().timestamp()
                
                # Get function from registry
                func = self.broker.function_registry.get(task.func_name)
                if func is None:
                    raise ValueError(f"Function '{task.func_name}' not found in registry")
                
                print(f"[WORKER-{self.worker_id}] Picked up task {task.task_id} ({task.func_name})")
                
                # Execute function
                result.result = func(*task.args, **task.kwargs)
                result.status = TaskStatus.SUCCESS
                result.completed_at = datetime.now().timestamp()
                
                print(f"[WORKER-{self.worker_id}] Task {task.task_id} completed in {result.duration_str} — result: {result.result}")
                
                return result
            
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                result.retry_count = retry_count
                
                if retry_count <= task.retry_limit:
                    # Calculate backoff delay
                    delay = self.backoff.get_delay(retry_count - 1)
                    
                    print(f"[WORKER-{self.worker_id}] Task {task.task_id} FAILED ({e.__class__.__name__}) — retry {retry_count}/{task.retry_limit} in {delay:.1f}s")
                    
                    time.sleep(delay)
                else:
                    # Max retries exceeded
                    result.status = TaskStatus.DEAD_LETTER
                    result.error = last_error
                    result.completed_at = datetime.now().timestamp()
                    
                    print(f"[WORKER-{self.worker_id}] Task {task.task_id} DEAD_LETTER after {retry_count} retries")
                    
                    # Move to dead-letter queue
                    task.max_retries = retry_count
                    self.broker.move_to_dead_letter(task)
                    
                    return result
        
        return result
    
    def stop(self) -> None:
        """Stop the worker."""
        self.running = False


def run_worker(worker_id: int, broker) -> None:
    """Entry point for worker process."""
    worker = Worker(worker_id, broker)
    worker.run()
