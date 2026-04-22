"""
Data models for the task queue system.
Includes Task, TaskResult, and TaskStatus definitions.
"""

from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import pickle
import json


class TaskStatus(Enum):
    """Task lifecycle states."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    DEAD_LETTER = "DEAD_LETTER"


@dataclass
class Task:
    """Represents a task to be executed."""
    task_id: str
    func_name: str
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    retry_limit: int = 3
    max_retries: int = field(default=0, init=False)
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'task_id': self.task_id,
            'func_name': self.func_name,
            'args': self.args,
            'kwargs': self.kwargs,
            'retry_limit': self.retry_limit,
            'max_retries': self.max_retries,
            'created_at': self.created_at,
        }
    
    def __repr__(self) -> str:
        return f"Task(id={self.task_id[:6]}, func={self.func_name}, retries={self.max_retries}/{self.retry_limit})"


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def duration_str(self) -> str:
        """Format duration as string."""
        if self.duration is None:
            return "—"
        return f"{self.duration:.2f}s"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'retry_count': self.retry_count,
            'duration': self.duration,
        }
    
    def __repr__(self) -> str:
        if self.status == TaskStatus.SUCCESS:
            return f"TaskResult(id={self.task_id[:6]}, status={self.status.value}, duration={self.duration_str})"
        elif self.status == TaskStatus.FAILED or self.status == TaskStatus.DEAD_LETTER:
            return f"TaskResult(id={self.task_id[:6]}, status={self.status.value}, error={self.error}, retries={self.retry_count})"
        else:
            return f"TaskResult(id={self.task_id[:6]}, status={self.status.value})"


@dataclass
class WorkerStats:
    """Worker process statistics."""
    worker_id: int
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    total_time: float = 0.0
    
    @property
    def avg_time(self) -> float:
        """Average task execution time."""
        if self.successful_tasks == 0:
            return 0.0
        return self.total_time / self.successful_tasks
    
    def __repr__(self) -> str:
        return (f"WorkerStats(id={self.worker_id}, tasks={self.total_tasks}, "
                f"success={self.successful_tasks}, failed={self.failed_tasks}, avg_time={self.avg_time:.2f}s)")
