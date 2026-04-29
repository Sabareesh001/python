"""
Output Formatting and Diff Display

Format test results with colors and readable diffs.
"""

from typing import List, Dict, Any
from enum import Enum


class Color:
    """ANSI color codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"


class TestStatus(Enum):
    """Test result status."""
    PASSED = "PASS"
    FAILED = "FAIL"
    SKIPPED = "SKIP"


class TestResult:
    """Represents the result of a single test."""
    
    def __init__(self, test_name: str, status: TestStatus, time_ms: float = 0):
        self.test_name = test_name
        self.status = status
        self.time_ms = time_ms
        self.error = None
        self.error_line = None
    
    def set_error(self, error: Exception, line: int = None):
        """Set error information."""
        self.error = str(error)
        self.error_line = line
    
    def format_result(self, width: int = 80) -> str:
        """Format this result as a string."""
        # Status indicator with color
        if self.status == TestStatus.PASSED:
            status_str = f"{Color.GREEN}✓ PASS{Color.RESET}"
        elif self.status == TestStatus.FAILED:
            status_str = f"{Color.RED}✗ FAIL{Color.RESET}"
        else:
            status_str = f"{Color.YELLOW}⊘ SKIP{Color.RESET}"
        
        # Time
        time_str = f"[{self.time_ms:6.2f}s]"
        
        # Determine spacing
        name_width = width - len(status_str) - len(time_str) - 10
        
        result = f"  {status_str:20} {self.test_name:{name_width}} {time_str}"
        
        # Add error details if present
        if self.error:
            error_lines = self.error.split("\n")
            for error_line in error_lines[:3]:  # Show first 3 lines
                result += f"\n        {Color.RED}{error_line.strip()}{Color.RESET}"
            if len(error_lines) > 3:
                result += f"\n        {Color.RED}...{Color.RESET}"
        
        return result


class TestReport:
    """Aggregate report of test results."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.total_time_ms = 0
        self.slowest_test = None
    
    def add_result(self, result: TestResult):
        """Add a test result."""
        self.results.append(result)
        
        if self.slowest_test is None or result.time_ms > self.slowest_test.time_ms:
            self.slowest_test = result
    
    def get_summary(self) -> Dict[str, int]:
        """Get count of each status."""
        return {
            "passed": sum(1 for r in self.results if r.status == TestStatus.PASSED),
            "failed": sum(1 for r in self.results if r.status == TestStatus.FAILED),
            "skipped": sum(1 for r in self.results if r.status == TestStatus.SKIPPED),
            "total": len(self.results),
        }
    
    def format_report(self) -> str:
        """Format the full test report."""
        lines = []
        
        # Header
        lines.append("")
        lines.append(f"{Color.BOLD}=== Test Results ==={Color.RESET}")
        lines.append("")
        
        # Results
        for result in self.results:
            lines.append(result.format_result())
        
        # Summary
        lines.append("")
        summary = self.get_summary()
        
        status_color = (Color.GREEN if summary["failed"] == 0 else Color.RED)
        
        summary_line = (f"{status_color}{Color.BOLD}"
                       f"{summary['total']} tests | "
                       f"{summary['passed']} passed | "
                       f"{summary['failed']} failed | "
                       f"{summary['skipped']} skipped"
                       f"{Color.RESET}")
        lines.append(summary_line)
        
        if self.slowest_test:
            lines.append(f"Slowest: {self.slowest_test.test_name} "
                        f"({self.slowest_test.time_ms:.2f}s)")
        
        lines.append(f"Total time: {self.total_time_ms:.2f}s")
        
        lines.append("")
        
        return "\n".join(lines)


class Formatter:
    """Test output formatter."""
    
    @staticmethod
    def format_test_name(test_name: str, params: List[Any] = None) -> str:
        """Format test name with optional parameters."""
        if params:
            params_str = ", ".join(str(p) for p in params)
            return f"{test_name}[{params_str}]"
        return test_name
    
    @staticmethod
    def format_diff(expected: Any, actual: Any) -> str:
        """Format a diff between expected and actual values."""
        exp_str = str(expected)
        act_str = str(actual)
        
        if len(exp_str) > 100:
            exp_str = exp_str[:97] + "..."
        if len(act_str) > 100:
            act_str = act_str[:97] + "..."
        
        return (f"Expected: {Color.GREEN}{exp_str}{Color.RESET}\n"
               f"Actual:   {Color.RED}{act_str}{Color.RESET}")
    
    @staticmethod
    def format_exception(exc: Exception) -> str:
        """Format exception for display."""
        exc_type = type(exc).__name__
        exc_msg = str(exc)
        return f"{Color.RED}{exc_type}: {exc_msg}{Color.RESET}"


# Test
if __name__ == "__main__":
    print("Testing Test Output Formatting\n")
    
    # Create results
    result1 = TestResult("test_addition", TestStatus.PASSED, 0.02)
    result2 = TestResult("test_subtraction", TestStatus.PASSED, 0.01)
    result3 = TestResult("test_division", TestStatus.FAILED, 0.03)
    result3.set_error(AssertionError("Expected 2, got 0"), line=42)
    result4 = TestResult("test_multiply", TestStatus.SKIPPED, 0.0)
    
    # Create report
    report = TestReport()
    for result in [result1, result2, result3, result4]:
        report.add_result(result)
    
    report.total_time_ms = 0.08
    
    # Print
    print(report.format_report())
