"""
Assertion Introspection and Analysis

Parse and display detailed assertion failures with variable inspection.
"""

import ast
import inspect
from typing import Any, Tuple, Optional


class AssertionAnalyzer:
    """Analyzes failed assertions to provide detailed output."""
    
    @staticmethod
    def get_assertion_source(func, line_number: int) -> Optional[str]:
        """Get the source code of an assertion at a specific line."""
        try:
            source_lines = inspect.getsourcelines(func)[0]
            # Line number is 1-indexed, but list is 0-indexed
            if 0 <= line_number - 1 < len(source_lines):
                return source_lines[line_number - 1].strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def parse_assertion(assertion_source: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse an assertion statement to extract the comparison.
        
        Example: "assert response.status == 401"
        Returns: ("response.status", "401")
        """
        if not assertion_source.startswith("assert "):
            return None, None
        
        expr = assertion_source[7:].strip()  # Remove 'assert '
        
        # Try to find comparison operators
        for op in ["==", "!=", "<", ">", "<=", ">=", "in", "not in", "is", "is not"]:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
        
        return expr, None
    
    @staticmethod
    def format_failure(assertion_source: str, left_val: Any, right_val: Any,
                      operator: str = "==") -> str:
        """Format an assertion failure message."""
        lines = []
        lines.append(f"AssertionError: Expected {right_val}, got {left_val}")
        lines.append(f"  |  assert {left_val} {operator} {right_val}")
        
        # Show variable inspection
        if left_val != right_val:
            left_type = type(left_val).__name__
            right_type = type(right_val).__name__
            lines.append(f"  |         |{' ' * len(str(left_val))}|")
            lines.append(f"  |         {left_val}{' ' * len(str(left_val))} "
                        f"{right_val}")
            lines.append(f"  |       ({left_type:10}) ({right_type})")
        
        return "\n".join(lines)


class Assertion:
    """Wrapper for assertion with introspection."""
    
    def __init__(self, condition: bool, message: str = ""):
        self.condition = condition
        self.message = message
    
    def __bool__(self):
        if not self.condition:
            raise AssertionError(self.message)
        return True


def custom_assert(condition: bool, message: str = "") -> bool:
    """Enhanced assert function with better error messages."""
    if not condition:
        raise AssertionError(message)
    return True


# Example introspection helpers
class AssertionContext:
    """Context for running assertions with introspection."""
    
    def __init__(self):
        self.failures = []
    
    def assert_equal(self, actual: Any, expected: Any, msg: str = ""):
        """Assert that two values are equal with detailed output."""
        if actual != expected:
            full_msg = msg or f"Expected {expected}, got {actual}"
            formatted = AssertionAnalyzer.format_failure(
                f"assert {actual} == {expected}",
                actual,
                expected,
                "=="
            )
            self.failures.append(formatted)
            raise AssertionError(formatted)
        return True
    
    def assert_true(self, condition: bool, msg: str = ""):
        """Assert that condition is True."""
        if not condition:
            raise AssertionError(msg or "Expected True")
        return True
    
    def assert_false(self, condition: bool, msg: str = ""):
        """Assert that condition is False."""
        if condition:
            raise AssertionError(msg or "Expected False")
        return True
    
    def assert_raises(self, exception_type, func, *args, **kwargs):
        """Assert that a function raises a specific exception."""
        try:
            func(*args, **kwargs)
            raise AssertionError(f"Expected {exception_type.__name__} but no exception was raised")
        except exception_type:
            return True
        except Exception as e:
            raise AssertionError(f"Expected {exception_type.__name__} but got {type(e).__name__}: {e}")


# Test
if __name__ == "__main__":
    analyzer = AssertionAnalyzer()
    
    print("Testing Assertion Analyzer\n")
    
    # Parse assertion
    left, right = analyzer.parse_assertion("assert response.status == 401")
    print(f"Parsed: '{left}' == '{right}'")
    
    # Format failure
    failure = analyzer.format_failure(
        "assert response.status == 401",
        200,
        401,
        "=="
    )
    print(f"\nFormatted failure:\n{failure}")
    
    # Use AssertionContext
    ctx = AssertionContext()
    try:
        ctx.assert_equal(200, 401, "Status code mismatch")
    except AssertionError as e:
        print(f"\nCaught: {e}")
