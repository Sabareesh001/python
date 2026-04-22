"""
Example usage of the distributed task queue system.
Demonstrates producer, workers, retries, dead-letter queue, and dashboard.
"""

import time
import multiprocessing
import threading
from broker import Broker
from backend import InMemoryBackend
from worker import Worker
from dashboard import Dashboard
import random


# --- Task Functions (to be executed by workers) ---

def generate_thumbnail(image_id: int, size: tuple) -> str:
    """Simulate thumbnail generation."""
    time.sleep(random.uniform(0.5, 1.5))
    return f"/thumbs/{image_id}_{size[0]}x{size[1]}.jpg"


def send_email(to: str, template: str) -> str:
    """Simulate email sending with occasional failures."""
    # Simulate occasional failures
    if random.random() < 0.6:
        raise ConnectionError("SMTP connection failed")
    
    time.sleep(random.uniform(0.5, 2.0))
    return f"email_sent_to_{to}"


def process_payment(order_id: int, amount: float) -> str:
    """Simulate payment processing."""
    time.sleep(random.uniform(1.0, 2.5))
    if random.random() < 0.3:
        raise ValueError("Payment validation failed")
    return f"payment_processed_${amount}"


def fetch_report(report_id: str) -> str:
    """Simulate report generation."""
    time.sleep(random.uniform(2.0, 3.0))
    return f"report_{report_id}.pdf"


def run_worker_thread(worker_id: int, broker) -> None:
    """Run worker in a thread (avoids Windows multiprocessing pickle issues)."""
    worker = Worker(worker_id, broker)
    worker.run()


# --- Main Demo ---

def main():
    print("=" * 70)
    print("DISTRIBUTED TASK QUEUE SYSTEM")
    print("=" * 70)
    print()
    
    # Create broker with in-memory backend
    backend = InMemoryBackend()
    broker = Broker(backend)
    
    # Register task functions
    broker.register_function(generate_thumbnail, "generate_thumbnail")
    broker.register_function(send_email, "send_email")
    broker.register_function(process_payment, "process_payment")
    broker.register_function(fetch_report, "fetch_report")
    
    print("\n" + "=" * 70)
    print("STEP 1: Starting Worker Processes")
    print("=" * 70)
    print()
    
    # Start worker processes using threading instead of multiprocessing
    # to avoid pickle issues with threading locks on Windows
    import threading
    
    num_workers = 3
    threads = []
    for i in range(1, num_workers + 1):
        t = threading.Thread(target=run_worker_thread, args=(i, broker), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(0.5)  # Let workers register
    
    print("\n" + "=" * 70)
    print("STEP 2: Enqueueing Tasks (Producer)")
    print("=" * 70)
    print()
    
    # Enqueue tasks
    tasks = [
        broker.enqueue("generate_thumbnail", 4521, (256, 256)),
        broker.enqueue("generate_thumbnail", 4522, (512, 512)),
        broker.enqueue("send_email", to="alice@example.com", template="welcome", retry_limit=3),
        broker.enqueue("send_email", to="bob@example.com", template="reset", retry_limit=3),
        broker.enqueue("process_payment", 1001, 99.99, retry_limit=2),
        broker.enqueue("fetch_report", "daily_summary", retry_limit=1),
    ]
    
    print()
    print("=" * 70)
    print("STEP 3: Waiting for Tasks to Complete")
    print("=" * 70)
    print()
    
    # Wait for all tasks to complete
    time.sleep(15)
    
    broker.print_status()
    
    print()
    print("=" * 70)
    print("STEP 4: Task Results Dashboard")
    print("=" * 70)
    
    Dashboard.print_full_dashboard(broker)
    
    print()
    print("=" * 70)
    print("STEP 5: Dead-Letter Queue")
    print("=" * 70)
    print()
    
    dead_letters = broker.queues["default"].get_dead_letters()
    if dead_letters:
        print(f"Dead-letter tasks ({len(dead_letters)} total):")
        for task in dead_letters:
            result = broker.get_result(task.task_id)
            print(f"  - Task {task.task_id}: {task.func_name} (retries: {task.max_retries}, error: {result.error if result else 'N/A'})")
    else:
        print("No dead-letter tasks.")
    
    print()
    
    # Wait for worker threads to finish
    for t in threads:
        t.join(timeout=1)
    
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
