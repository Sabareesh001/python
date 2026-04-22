"""
Dashboard for viewing task queue status and metrics.
"""

from typing import Dict, List
from models import TaskStatus, TaskResult
from tabulate import tabulate


class Dashboard:
    """Displays task queue metrics and status."""
    
    @staticmethod
    def print_task_results(results: Dict[str, TaskResult], limit: int = 10) -> None:
        """Print task results as a table."""
        print("\n" + "=" * 90)
        print("Task Results Dashboard")
        print("=" * 90)
        
        if not results:
            print("No results available.")
            return
        
        # Sort by creation time (assuming we can get it from results)
        sorted_results = sorted(results.items(), key=lambda x: x[1].task_id)[-limit:]
        
        rows = []
        for task_id, result in sorted_results:
            rows.append([
                task_id[:8],
                result.task_id.split('_')[0][:20] if '_' in result.task_id else 'task',
                result.status.value,
                result.retry_count,
                result.duration_str,
                result.error[:40] if result.error else result.result if result.result else '—',
            ])
        
        headers = ["Task ID", "Function", "Status", "Retries", "Duration", "Result/Error"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    @staticmethod
    def print_worker_stats(worker_stats: Dict[int, any]) -> None:
        """Print worker statistics."""
        print("\n" + "=" * 90)
        print("Worker Statistics")
        print("=" * 90)
        
        if not worker_stats:
            print("No worker statistics available.")
            return
        
        rows = []
        total_tasks = 0
        total_success = 0
        total_failed = 0
        
        for worker_id, stats in sorted(worker_stats.items()):
            rows.append([
                f"Worker-{stats.worker_id}",
                stats.total_tasks,
                stats.successful_tasks,
                stats.failed_tasks,
                f"{stats.avg_time:.2f}s",
            ])
            total_tasks += stats.total_tasks
            total_success += stats.successful_tasks
            total_failed += stats.failed_tasks
        
        # Add totals row
        rows.append([
            "TOTAL",
            total_tasks,
            total_success,
            total_failed,
            "—",
        ])
        
        headers = ["Worker", "Total Tasks", "Successful", "Failed", "Avg Time"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    @staticmethod
    def print_status_summary(broker) -> None:
        """Print overall broker status."""
        print("\n" + "=" * 90)
        print("Broker Status Summary")
        print("=" * 90)
        
        status = broker.get_status()
        results = broker.get_all_results()
        
        # Count by status
        status_counts = {}
        for result in results.values():
            status_name = result.status.value
            status_counts[status_name] = status_counts.get(status_name, 0) + 1
        
        print(f"Connected Workers: {status['connected_workers']}")
        print(f"Pending Tasks: {status['pending_tasks']}")
        print(f"Dead Letter Tasks: {status['dead_letter_tasks']}")
        print(f"Total Completed Tasks: {len(results)}")
        
        if status_counts:
            print("\nTask Status Breakdown:")
            for status_name in sorted(status_counts.keys()):
                count = status_counts[status_name]
                print(f"  - {status_name}: {count}")
    
    @staticmethod
    def print_full_dashboard(broker) -> None:
        """Print complete dashboard."""
        Dashboard.print_status_summary(broker)
        Dashboard.print_task_results(broker.get_all_results())
        Dashboard.print_worker_stats(broker.worker_stats)
