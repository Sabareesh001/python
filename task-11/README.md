# Task 11: Automated Testing Framework

A lightweight, custom test framework built from scratch with test discovery, fixtures, parameterization, assertion introspection, and parallel execution.

## Features

- **Test Discovery**: Auto-discovers test functions by naming convention (`test_*`) or decorator
- **Fixtures**: Setup/teardown with session, module, and function scopes
- **Parameterized Tests**: Run same test with multiple input sets
- **Assertion Introspection**: Display detailed diff of expected vs. actual values
- **Parallel Execution**: Run tests across N worker processes
- **Performance Tracking**: Measure and report test timing
- **Skip Support**: Conditionally skip tests with reasons
- **Rich Output**: Colored, formatted test result reporting
- **Exception Handling**: Capture and display stack traces

## Project Structure

```
task-11/
├── README.md
├── requirements.txt
├── decorators.py          # Test decorators (@test, @fixture, @skip, @parametrize)
├── assertions.py          # Assertion introspection and diffs
├── formatter.py           # Output formatting, colors, diffs
├── framework.py           # Test discovery and execution engine
├── runner.py              # CLI test runner
├── example_tests.py       # Example test suite
└── conftest.py            # Shared fixtures (optional)
```

## How It Works

### 1. Test Discovery

- Scanner walks through test files
- Finds functions matching `test_*` pattern
- Collects fixtures by looking for `@fixture` decorator
- Extracts metadata (params, skip reason, etc.)

### 2. Fixture Resolution

- Build dependency graph of fixtures
- Instantiate in correct order (session → module → function)
- Pass fixtures to test functions via inspection

### 3. Test Execution

- Create worker processes for parallel execution
- Each worker runs assigned tests
- Capture output, timing, and exceptions
- Stream results back to main process

### 4. Assertion Introspection

- Parse assertion expression from source code
- Evaluate left and right sides
- Display comparison with variable inspection

### 5. Result Reporting

- Aggregate results from all workers
- Sort by test name
- Display with color coding (pass=green, fail=red, skip=yellow)
- Show timing information

## Running Tests

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run tests with CLI runner

```bash
# Run all tests
python runner.py

# Run with verbosity
python runner.py --verbose

# Run with 4 parallel workers
python runner.py --parallel 4

# Run specific test file
python runner.py tests/test_auth.py

# Run specific test
python runner.py tests/test_auth.py::test_login_valid
```

Expected output:

```
=== Test Discovery ===
Found 23 tests across 5 modules
Fixtures loaded: db_connection (session), temp_dir (function), mock_api (function)

=== Execution (4 workers) ===
tests/test_auth.py
  PASS  test_login_valid_credentials                    [0.02s]
  PASS  test_login_invalid_password                     [0.01s]
  FAIL  test_login_expired_token                        [0.03s]
        AssertionError: Expected status=401, got status=200
        at tests/test_auth.py:45

tests/test_cart.py
  PASS  test_add_item[product_id=1, qty=1]              [0.01s]
  PASS  test_add_item[product_id=2, qty=5]              [0.01s]
  PASS  test_add_item[product_id=99, qty=0]             [0.01s]
  SKIP  test_checkout_stripe (skipped: no API key)      [0.00s]

=== Summary ===
23 tests | 20 passed | 2 failed | 1 skipped
Total time: 0.48s (parallel across 4 workers)
Slowest: test_full_integration (0.21s)
```

## Writing Tests

### Basic Test

```python
@test
def test_addition():
    assert 2 + 2 == 4
```

### Test with Fixtures

```python
@fixture
def temp_dir():
    dir = create_temp_dir()
    yield dir
    cleanup(dir)

@test
def test_file_write(temp_dir):
    file = open(f"{temp_dir}/test.txt", "w")
    file.write("hello")
    file.close()
    assert os.path.exists(f"{temp_dir}/test.txt")
```

### Parameterized Tests

```python
@parametrize([
    (2, 2, 4),
    (3, 4, 7),
    (5, 5, 10),
])
@test
def test_add(a, b, expected):
    assert a + b == expected
```

### Skip Tests

```python
@skip("API key not configured")
@test
def test_api_call():
    ...
```

## Architecture Patterns

- **Decorator Pattern**: `@test`, `@fixture`, `@parametrize` for metadata
- **Reflection**: `inspect` module for function introspection
- **Multiprocessing**: Worker pool for parallel test execution
- **Context Managers**: Fixture setup/teardown
- **AST Parsing**: Extract assertion expressions for introspection
- **Exception Capture**: Traceback formatting for debugging

## Learning Outcomes

- ✅ Decorators and metadata
- ✅ Reflection with `inspect` module
- ✅ Multiprocessing and worker pools
- ✅ Exception handling and tracebacks
- ✅ AST parsing for assertion introspection
- ✅ Context managers for fixtures
- ✅ Test discovery and plugin architecture
- ✅ Command-line interface building
