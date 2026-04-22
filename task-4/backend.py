"""
Result backend for storing task execution results.
Supports in-memory storage and SQLite persistence.
"""

import sqlite3
import json
from typing import Optional, Dict, List, Any
from datetime import datetime
from models import TaskResult, TaskStatus


class ResultBackend:
    """Base class for result backends."""
    
    def set(self, task_id: str, result: TaskResult) -> None:
        """Store task result."""
        raise NotImplementedError
    
    def get(self, task_id: str) -> Optional[TaskResult]:
        """Retrieve task result."""
        raise NotImplementedError
    
    def delete(self, task_id: str) -> bool:
        """Delete task result."""
        raise NotImplementedError
    
    def exists(self, task_id: str) -> bool:
        """Check if result exists."""
        raise NotImplementedError
    
    def get_all(self) -> Dict[str, TaskResult]:
        """Get all stored results."""
        raise NotImplementedError


class InMemoryBackend(ResultBackend):
    """In-memory result storage."""
    
    def __init__(self):
        self._results: Dict[str, TaskResult] = {}
    
    def set(self, task_id: str, result: TaskResult) -> None:
        self._results[task_id] = result
    
    def get(self, task_id: str) -> Optional[TaskResult]:
        return self._results.get(task_id)
    
    def delete(self, task_id: str) -> bool:
        if task_id in self._results:
            del self._results[task_id]
            return True
        return False
    
    def exists(self, task_id: str) -> bool:
        return task_id in self._results
    
    def get_all(self) -> Dict[str, TaskResult]:
        return dict(self._results)


class SQLiteBackend(ResultBackend):
    """SQLite-based persistent result storage."""
    
    def __init__(self, db_path: str = "task_results.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_results (
                    task_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    result TEXT,
                    error TEXT,
                    started_at REAL,
                    completed_at REAL,
                    retry_count INTEGER,
                    created_at REAL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def set(self, task_id: str, result: TaskResult) -> None:
        """Store result in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Try to serialize result
            try:
                result_json = json.dumps(result.result)
            except (TypeError, json.JSONDecodeError):
                result_json = str(result.result)
            
            cursor.execute("""
                INSERT OR REPLACE INTO task_results
                (task_id, status, result, error, started_at, completed_at, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                result.status.value,
                result_json,
                result.error,
                result.started_at,
                result.completed_at,
                result.retry_count,
            ))
            conn.commit()
    
    def get(self, task_id: str) -> Optional[TaskResult]:
        """Retrieve result from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, result, error, started_at, completed_at, retry_count
                FROM task_results WHERE task_id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            status, result_str, error, started_at, completed_at, retry_count = row
            
            # Try to deserialize result
            try:
                result = json.loads(result_str) if result_str else None
            except json.JSONDecodeError:
                result = result_str
            
            return TaskResult(
                task_id=task_id,
                status=TaskStatus(status),
                result=result,
                error=error,
                started_at=started_at,
                completed_at=completed_at,
                retry_count=retry_count,
            )
    
    def delete(self, task_id: str) -> bool:
        """Delete result from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM task_results WHERE task_id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def exists(self, task_id: str) -> bool:
        """Check if result exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM task_results WHERE task_id = ?", (task_id,))
            return cursor.fetchone() is not None
    
    def get_all(self) -> Dict[str, TaskResult]:
        """Get all stored results."""
        results = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_id, status, result, error, started_at, completed_at, retry_count
                FROM task_results
            """)
            
            for row in cursor.fetchall():
                task_id, status, result_str, error, started_at, completed_at, retry_count = row
                
                try:
                    result = json.loads(result_str) if result_str else None
                except json.JSONDecodeError:
                    result = result_str
                
                results[task_id] = TaskResult(
                    task_id=task_id,
                    status=TaskStatus(status),
                    result=result,
                    error=error,
                    started_at=started_at,
                    completed_at=completed_at,
                    retry_count=retry_count,
                )
        
        return results
