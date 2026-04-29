"""
Example Test Suite

Demonstrates the testing framework with various test types.
"""

from decorators import test, fixture, skip, parametrize
from assertions import AssertionContext
import time


# ============ Fixtures ============

@fixture(scope="function")
def temp_list():
    """Fixture that provides a temporary list."""
    lst = []
    yield lst
    lst.clear()


@fixture(scope="function")
def counter():
    """Fixture that provides a counter."""
    class Counter:
        def __init__(self):
            self.value = 0
        
        def increment(self):
            self.value += 1
        
        def reset(self):
            self.value = 0
    
    yield Counter()


# ============ Basic Tests ============

@test
def test_addition():
    """Test basic addition."""
    assert 2 + 2 == 4


@test
def test_subtraction():
    """Test basic subtraction."""
    assert 5 - 3 == 2


@test
def test_multiplication():
    """Test basic multiplication."""
    result = 3 * 4
    assert result == 12


# ============ Tests with Fixtures ============

@test
def test_list_append(temp_list):
    """Test list append with fixture."""
    temp_list.append(1)
    temp_list.append(2)
    assert len(temp_list) == 2
    assert temp_list[0] == 1


@test
def test_list_operations(temp_list):
    """Test multiple list operations."""
    temp_list.extend([1, 2, 3])
    assert len(temp_list) == 3
    assert sum(temp_list) == 6


@test
def test_counter_increment(counter):
    """Test counter increment."""
    counter.increment()
    counter.increment()
    assert counter.value == 2


# ============ Parameterized Tests ============

@parametrize([
    (1, 2, 3),
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
])
@test
def test_add(a, b, expected):
    """Parameterized test for addition."""
    assert a + b == expected


@parametrize([
    ("hello", 5),
    ("world", 5),
    ("a", 1),
    ("", 0),
])
@test
def test_string_length(s, expected_len):
    """Parameterized test for string length."""
    assert len(s) == expected_len


@parametrize([
    ([1, 2, 3], 3),
    ([], 0),
    ([1], 1),
])
@test
def test_list_length(lst, expected_len):
    """Parameterized test for list length."""
    assert len(lst) == expected_len


# ============ Tests with Assertions ============

@test
def test_dict_access():
    """Test dictionary operations."""
    d = {"name": "Alice", "age": 30}
    assert d["name"] == "Alice"
    assert d.get("missing") is None


@test
def test_boolean_logic():
    """Test boolean logic."""
    assert True
    assert not False
    assert (True and True)
    assert (True or False)


# ============ Tests that Fail (for demo) ============

@test
def test_string_contains():
    """Test string containment."""
    s = "Hello, World!"
    assert "Hello" in s
    assert "world" not in s  # Case sensitive


# ============ Skipped Tests ============

@skip("Not implemented yet")
@test
def test_future_feature():
    """This test is skipped."""
    raise NotImplementedError("Coming soon")


@skip("API key not configured")
@test
def test_api_call():
    """This test requires external setup."""
    # api.call()
    pass


# ============ Tests with Timing ============

@test
def test_fast_operation():
    """Fast test."""
    result = sum(range(100))
    assert result == 4950


@test
def test_slower_operation():
    """Slightly slower test."""
    # Simulate some work
    time.sleep(0.01)
    result = sum(range(1000))
    assert result == 499500


if __name__ == "__main__":
    # Run with: python runner.py example_tests.py
    print("Run with: python runner.py example_tests.py")
