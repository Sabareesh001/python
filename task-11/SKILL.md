# Skill: Task 11 - Automated Testing Framework

This skill provides comprehensive guidance for building and extending the custom testing framework.

## Overview

Task 11 implements a lightweight test framework from scratch with test discovery, fixtures, parameterization, assertion introspection, parallel execution, and rich output formatting. Similar to pytest but built from first principles.

## Project Architecture

### Components

1. **decorators.py**: @test, @fixture, @skip, @parametrize decorators
2. **assertions.py**: Custom assertion methods with introspection and diff display
3. **formatter.py**: Colored output, diff formatting, result reporting
4. **framework.py**: Test discovery, fixture resolution, execution engine
5. **runner.py**: CLI runner with worker process management
6. **example_tests.py**: Comprehensive examples of all framework features

## Core Concepts

### Test Discovery

Scanner finds functions matching `test_*` naming convention or @test decorator:

```python
def test_addition():
    assert 1 + 1 == 2

@test
def custom_test_name():
    assert True
```

### Fixtures

Setup/teardown functions with multiple scopes:

```python
@fixture(scope="function")
def temp_list():
    lst = []
    yield lst  # Test gets this value
    lst.clear()  # Teardown runs after test

def test_something(temp_list):
    temp_list.append(1)  # Fixture auto-injected
```

Scopes:

- **function**: Fresh fixture per test (default)
- **module**: Fixture shared across all tests in file
- **session**: Fixture shared across entire test run

### Parameterization

Run same test with multiple input sets:

```python
@parametrize("input,expected", [
    (1, 2, 3),
    (2, 3, 5),
    (0, 0, 0),
])
def test_add(a, b, expected):
    assert a + b == expected
```

Creates 3 separate test runs with different inputs.

### Assertion Introspection

Custom assertions show detailed diffs:

```python
# Framework displays:
# Expected: 5
# Actual:   3
# Diff:     -5 +3
assert 3 == 5  # Shows both values, not just "False"
```

## Running Tests

### Basic Usage

```bash
cd task-11
python runner.py example_tests.py
```

Output shows:

- Test count and discovery results
- Pass/fail/skip counts
- Execution time per test
- Slowest tests identified

### Filtering Tests

```bash
python runner.py example_tests.py -k "test_string"  # Run matching tests
python runner.py example_tests.py -v              # Verbose output
```

### Parallel Execution

```bash
python runner.py example_tests.py -n 4  # Use 4 worker processes
```

## Creating Test Suites

### Basic Test Structure

```python
from decorators import test, fixture, parametrize, skip
from assertions import assert_equal

def test_basic_math():
    assert 2 + 2 == 4

@skip("Not ready yet")
def test_future_feature():
    pass

@parametrize("x,expected", [(1, 2), (2, 4)])
def test_double(x, expected):
    assert x * 2 == expected

@fixture(scope="function")
def counter():
    return {"count": 0}

def test_with_fixture(counter):
    counter["count"] += 1
    assert counter["count"] == 1
```

## Common Tasks & Solutions

### Adding New Fixture Scopes

Modify `framework.py` fixture resolution:

1. Add scope to fixture decorator
2. Update FixtureResolver to handle scope lifecycle
3. Store fixtures in appropriate cache (session, module, or function)

### Implementing Assertion Helpers

Add custom assertions to `assertions.py`:

```python
def assert_in_range(value, min_val, max_val):
    if not (min_val <= value <= max_val):
        raise AssertionError(
            f"Expected {value} to be in range [{min_val}, {max_val}]"
        )
```

### Debugging Test Failures

**Problem**: Fixture not injected to test

- Check parameter name matches fixture name exactly
- Verify @fixture decorator is applied
- Check fixture scope is compatible with test scope

**Problem**: Parameterized test not running all variants

- Verify @parametrize has correct format: `("arg_names", [values])`
- Check all value tuples match number of arguments
- Test name should include parameter values in output

**Problem**: Test timeout or hangs

- Use `@skip()` to skip slow tests during development
- Add timeout handling in `runner.py` worker process
- Break long tests into smaller unit tests

## Key Files to Understand

- `decorators.py`: How @test, @fixture, @parametrize work
- `assertions.py`: Introspection logic and diff generation
- `formatter.py`: Output coloring and formatting
- `framework.py` lines 1-50: Test discovery algorithm
- `framework.py` lines 50-150: Fixture resolution and injection
- `runner.py`: Worker process management and parallel execution

## Performance Tips

### Faster Test Runs

- Use `@skip()` for slow integration tests during development
- Mark slow tests with `@slow` decorator and skip by default
- Run tests in parallel with `-n` flag

### Memory Efficiency

- Clear large fixtures in teardown (yield statement)
- Use function-scoped fixtures instead of session-scoped when possible
- Process worker pools automatically clean up between tests

### Assertion Performance

- Avoid expensive introspection for every assertion
- Cache diff calculations for repeated assertions
- Lazy-load formatter only when assertion fails

## Example: Adding Custom Assertion

```python
# In assertions.py
def assert_list_equal(actual, expected):
    if actual != expected:
        diff = show_diff(actual, expected)
        raise AssertionError(f"Lists not equal:\n{diff}")

# In test file
def test_list_operations():
    result = [1, 2, 3]
    assert_list_equal(result, [1, 2, 3])
```

## Testing the Framework Itself

Run framework tests to verify changes:

```bash
python runner.py example_tests.py
# All 24 tests should pass (22 pass, 2 skip)
```
