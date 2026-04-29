"""
Test Decorators and Metadata

Defines decorators for marking tests, fixtures, and test parameters.
"""

from typing import Any, Callable, List, Optional


class TestMetadata:
    """Stores metadata about a test function."""
    
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.params = []  # Parameterized test cases
        self.skip_reason = None
        self.fixture_names = []
    
    def is_test(self) -> bool:
        """Whether this is marked as a test."""
        return hasattr(self.func, "_is_test") and self.func._is_test
    
    def is_fixture(self) -> bool:
        """Whether this is marked as a fixture."""
        return hasattr(self.func, "_is_fixture") and self.func._is_fixture
    
    def is_skipped(self) -> bool:
        """Whether this test is skipped."""
        return self.skip_reason is not None


def test(func: Callable) -> Callable:
    """
    Decorator to mark a function as a test.
    
    Usage:
        @test
        def test_something():
            assert True
    """
    func._is_test = True
    return func


def fixture(scope: str = "function"):
    """
    Decorator to mark a function as a fixture.
    
    Args:
        scope: 'function', 'module', or 'session'
    
    Usage:
        @fixture
        def temp_dir():
            d = create_dir()
            yield d
            cleanup(d)
    """
    def decorator(func: Callable) -> Callable:
        func._is_fixture = True
        func._fixture_scope = scope
        return func
    return decorator


def skip(reason: str = ""):
    """
    Decorator to skip a test.
    
    Usage:
        @skip("not implemented")
        @test
        def test_future_feature():
            ...
    """
    def decorator(func: Callable) -> Callable:
        func._skip_reason = reason
        return func
    return decorator


def parametrize(cases: List[tuple]):
    """
    Decorator to run a test with multiple parameter sets.
    
    Usage:
        @parametrize([
            (1, 2, 3),
            (4, 5, 9),
        ])
        @test
        def test_add(a, b, expected):
            assert a + b == expected
    """
    def decorator(func: Callable) -> Callable:
        func._parametrize_cases = cases
        return func
    return decorator


# Metadata registry
_test_registry = {}


def register_test(name: str, metadata: TestMetadata):
    """Register a test in the global registry."""
    _test_registry[name] = metadata


def get_registered_tests():
    """Get all registered tests."""
    return _test_registry.copy()


# Example usage
if __name__ == "__main__":
    @fixture
    def setup():
        print("Setting up fixture")
        yield "fixture_data"
        print("Tearing down fixture")
    
    @parametrize([
        (1, 2, 3),
        (2, 3, 5),
    ])
    @test
    def test_add(a, b, expected):
        assert a + b == expected
    
    @skip("Not implemented yet")
    @test
    def test_future_feature():
        pass
    
    print(f"test_add is marked as test: {hasattr(test_add, '_is_test')}")
    print(f"test_add has params: {hasattr(test_add, '_parametrize_cases')}")
    print(f"setup is fixture: {hasattr(setup, '_is_fixture')}")
    print(f"test_future_feature skip reason: {test_future_feature._skip_reason}")
