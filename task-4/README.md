# Distributed Task Queue

A production-ready distributed task queue system implementing producer-consumer patterns, exponential backoff retries, dead-letter queues, and persistent result storage.

## Architecture Overview

### Core Components

1. **Models** (`models.py`)
   - `Task`: Represents a queued task with metadata
   - `TaskResult`: Stores execution results
   - `TaskStatus`: Enum for task lifecycle states
   - `WorkerStats`: Worker performance metrics

2. **Result Backend** (`backend.py`)
   - `ResultBackend`: Abstract base class
   - `InMemoryBackend`: Fast volatile storage
   - `SQLiteBackend`: Persistent storage

3. **Broker** (`broker.py`)
   - `TaskQueue`: Thread-safe queue with dead-letter support
   - `Broker`: Central task manager and orchestrator

4. **Worker** (`worker.py`)
   - `ExponentialBackoff`: Retry delay calculation
   - `Worker`: Task execution process

5. **Dashboard** (`dashboard.py`)
   - Real-time metrics and status visualization

## Key Features

### 1. Producer-Consumer Pattern

**Producer (Enqueue Tasks):**

```python
broker.enqueue("send_email", to="bob@co.com", template="welcome")
# Output: Task queued: <Task id=b7d4e2 func=send_email status=PENDING>
```

**Consumer (Worker Processes):**

- Multiple worker processes poll the queue
- Execute tasks immediately upon availability
- Report results back to broker

### 2. Exponential Backoff Retries

Failed tasks automatically retry with exponential backoff:

```python
def send_email(to: str, template: str):
    if fails:
        raise ConnectionError("SMTP failed")

task = broker.enqueue("send_email", to="bob@co.com", template="welcome", retry_limit=3)

# Retry sequence:
# Attempt 1: fails
# Wait 1s (2^0 × 1)
# Attempt 2: fails
# Wait 2s (2^1 × 1)
# Attempt 3: fails
# Wait 4s (2^2 × 1)
# Attempt 4: move to dead-letter queue
```

**Output:**

```
[WORKER-2] Task b7d4e2 FAILED (SMTPConnectionError) — retry 1/3 in 1.0s
[WORKER-2] Task b7d4e2 FAILED (SMTPConnectionError) — retry 2/3 in 2.0s
[WORKER-2] Task b7d4e2 FAILED (SMTPConnectionError) — retry 3/3 in 4.0s
[WORKER-2] Task b7d4e2 DEAD_LETTER after 3 retries
```

### 3. Dead-Letter Queue (DLQ)

Tasks that exhaust retries move to a dead-letter queue for manual inspection:

```python
dead_letters = broker.queues["default"].get_dead_letters()
for task in dead_letters:
    result = broker.get_result(task.task_id)
    print(f"Task {task.task_id}: {result.error}")
```

**Use Cases:**

- Manual retry after fixing underlying issues
- Monitoring and alerting
- Post-mortem analysis
- Dead-letter task replay

### 4. Result Backend

**In-Memory Backend (Fast):**

```python
from backend import InMemoryBackend
backend = InMemoryBackend()
broker = Broker(backend)
```

**SQLite Backend (Persistent):**

```python
from backend import SQLiteBackend
backend = SQLiteBackend("task_results.db")
broker = Broker(backend)
```

### 5. Distributed Worker Processes

```python
# Start multiple workers
for i in range(1, 4):
    p = multiprocessing.Process(target=run_worker, args=(i, broker))
    p.start()

# Workers automatically:
# - Register with broker
# - Poll queue for tasks
# - Execute tasks in parallel
# - Handle retries independently
# - Report results to backend
```

### 6. Task Registration

```python
def generate_thumbnail(image_id: int, size: tuple) -> str:
    return f"/thumbs/{image_id}_{size[0]}x{size[1]}.jpg"

# Register callable
broker.register_function(generate_thumbnail, "generate_thumbnail")

# Enqueue task by name
broker.enqueue("generate_thumbnail", 4521, (256, 256))
```

### 7. Dashboard & Metrics

```python
# Full dashboard with all metrics
Dashboard.print_full_dashboard(broker)

# Individual views
Dashboard.print_status_summary(broker)
Dashboard.print_task_results(broker.get_all_results())
Dashboard.print_worker_stats(broker.worker_stats)
```

**Output:**

```
============================================================================
Broker Status Summary
============================================================================
Connected Workers: 3
Pending Tasks: 0
Dead Letter Tasks: 1
Total Completed Tasks: 6

Task Status Breakdown:
  - DEAD_LETTER: 1
  - SUCCESS: 5

============================================================================
Task Results Dashboard
============================================================================
+----------+------------+----------+---------+---------+-------+
| Task ID  | Function   | Status   | Retries | Duration| Result|
+----------+------------+----------+---------+---------+-------+
| a8f3c1   | thumbnail  | SUCCESS  | 0       | 1.34s   | /thumb|
| b7d4e2   | email      | SUCCESS  | 2       | 6.82s   | email |
| c9e5f3   | report     | DEAD_LTR | 3       | —       | timeout|
+----------+------------+----------+---------+---------+-------+

============================================================================
Worker Statistics
============================================================================
+----------+-------+-------+-------+--------+
| Worker   | Total | Succ  | Failed| AvgTim |
+----------+-------+-------+-------+--------+
| Worker-1 | 2     | 2     | 0     | 1.20s  |
| Worker-2 | 3     | 2     | 1     | 2.15s  |
| Worker-3 | 1     | 1     | 0     | 2.50s  |
| TOTAL    | 6     | 5     | 1     | —      |
+----------+-------+-------+-------+--------+
```

## Implementation Details

### Task Lifecycle

```
PENDING → RUNNING → SUCCESS (result stored)
              ↓
           FAILED → RETRYING → [retry sequence]
              ↓
         DEAD_LETTER (moved to DLQ after max retries)
```

### Thread Safety

All shared data structures protected by locks:

- Task queue uses `threading.RLock()`
- Worker stats use `threading.RLock()`
- Result backend is thread-safe

### Process Isolation

- Each worker is independent process
- Tasks serialized via pickle
- Results stored in backend (not shared memory)
- No race conditions or deadlocks

### Exponential Backoff Algorithm

```python
delay = base_delay × (2 ^ retry_count)
delay = min(delay, max_delay)

# Example: base=1s, max=60s
retry 1: delay = 1s
retry 2: delay = 2s
retry 3: delay = 4s
retry 4: delay = 8s
retry 5: delay = 16s
retry 6: delay = 32s
retry 7+: delay = 60s (capped)
```

## Advanced Usage

### Custom Result Backend

```python
class RedisBackend(ResultBackend):
    def __init__(self, redis_client):
        self.redis = redis_client

    def set(self, task_id: str, result: TaskResult):
        self.redis.setex(
            f"result:{task_id}",
            3600,  # 1 hour TTL
            json.dumps(result.to_dict())
        )

    def get(self, task_id: str) -> Optional[TaskResult]:
        data = self.redis.get(f"result:{task_id}")
        return TaskResult(**json.loads(data)) if data else None
```

### Task Priorities

```python
# Add priority support to TaskQueue
class PriorityTaskQueue(TaskQueue):
    def __init__(self):
        self._queue = PriorityQueue()  # Min-heap by priority

    def put(self, task: Task, priority: int = 0):
        self._queue.put((priority, task))
```

### Task Scheduling

```python
# Schedule task for later execution
from datetime import datetime, timedelta

scheduled_task = Task(...)
scheduled_task.execute_after = datetime.now() + timedelta(hours=1)

# Workers check execute_after before processing
```

## Code Statistics

- **models.py**: 80+ lines - Data models and enums
- **backend.py**: 120+ lines - Result persistence
- **broker.py**: 140+ lines - Task queue management
- **worker.py**: 110+ lines - Task execution with retries
- **dashboard.py**: 90+ lines - Metrics visualization
- **Total**: 550+ lines of core implementation

## Running the Example

```bash
python example.py
```

The example demonstrates:

- Producer enqueueing 6 different tasks
- 3 concurrent worker processes
- Automatic retries on failures
- Dead-letter queue tracking
- Comprehensive dashboard with metrics
- Worker statistics and task durations

## Key Concepts

✅ **Producer-Consumer**: Decoupled task submission and execution  
✅ **Exponential Backoff**: Intelligent retry delays reduce server load  
✅ **Dead-Letter Queue**: Failed tasks isolated for analysis  
✅ **Distributed Workers**: Parallel execution across processes  
✅ **Result Backend**: Flexible persistence (memory/SQL/Redis)  
✅ **Thread Safety**: No race conditions or deadlocks  
✅ **Metrics**: Real-time visibility into system health

## Design Patterns Used

- **Producer-Consumer**: Separate task submission from execution
- **Pub-Sub**: Workers subscribe to task queue
- **Retry Pattern**: Exponential backoff for transient failures
- **Circuit Breaker**: Dead-letter queue for cascading failures
- **Builder Pattern**: Task construction with fluent interface
- **Factory Pattern**: Backend instantiation
- **Metrics**: Observability and monitoring
