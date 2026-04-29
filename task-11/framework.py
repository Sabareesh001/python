"""
Test Framework Core

Discovers tests, resolves fixtures, and executes them.
"""

import os
import sys
import importlib.util
import inspect
import time
from pathlib import Path
from typing import List, Dict, Callable, Any, Optional, Tuple
from multiprocessing import Pool, cpu_count

from decorators import test, fixture, skip, parametrize
from formatter import TestResult, TestReport, TestStatus
from assertions import AssertionContext


class Fixture:
    """Represents a fixture with scope information."""
    
    def __init__(self, func: Callable, scope: str = "function"):
        self.func = func
        self.scope = scope
        self.name = func.__name__
        self.instance = None
        self.generator = None
    
    def setup(self):
        """Set up the fixture."""
        if inspect.isgeneratorfunction(self.func):
            self.generator = self.func()
            self.instance = next(self.generator)
        else:
            self.instance = self.func()
        return self.instance
    
    def teardown(self):
        """Tear down the fixture."""
        if self.generator:
            try:
                next(self.generator)
            except StopIteration:
                pass


class TestCase:
    """Represents a single test case."""
    
    def __init__(self, func: Callable, name: str, module_name: str,
                 params: Tuple = None):
        self.func = func
        self.name = name
        self.module_name = module_name
        self.params = params
        self.skip_reason = getattr(func, "_skip_reason", None)
    
    def get_full_name(self) -> str:
        """Get fully qualified test name."""
        if self.params:
            params_str = ", ".join(str(p) for p in self.params)
            return f"{self.name}[{params_str}]"
        return self.name


class TestDiscoverer:
    """Discovers tests in a directory or module."""
    
    def __init__(self, test_dir: str = "./"):
        self.test_dir = Path(test_dir)
        self.tests: List[TestCase] = []
        self.fixtures: Dict[str, Fixture] = {}
    
    def discover(self) -> List[TestCase]:
        """Discover all tests."""
        if self.test_dir.is_file():
            self._load_module(self.test_dir)
        else:
            for test_file in self.test_dir.rglob("test_*.py"):
                self._load_module(test_file)
        
        return self.tests
    
    def _load_module(self, file_path: Path):
        """Load a Python module and extract tests."""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if not spec or not spec.loader:
            return
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        
        # Extract fixtures
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, "_is_fixture"):
                scope = getattr(obj, "_fixture_scope", "function")
                self.fixtures[name] = Fixture(obj, scope)
        
        # Extract tests
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and hasattr(obj, "_is_test"):
                # Check for parametrization
                if hasattr(obj, "_parametrize_cases"):
                    for params in obj._parametrize_cases:
                        test_case = TestCase(
                            obj,
                            name,
                            file_path.stem,
                            params
                        )
                        self.tests.append(test_case)
                else:
                    test_case = TestCase(obj, name, file_path.stem)
                    self.tests.append(test_case)


class TestExecutor:
    """Executes individual tests."""
    
    def __init__(self, fixtures: Dict[str, Fixture]):
        self.fixtures = fixtures
        self.setup_fixtures = {}
    
    def execute(self, test_case: TestCase) -> Tuple[TestStatus, str, float]:
        """
        Execute a single test case.
        
        Returns:
            (status, error_message, execution_time)
        """
        start_time = time.time()
        
        # Check if skipped
        if test_case.skip_reason:
            elapsed = time.time() - start_time
            return TestStatus.SKIPPED, test_case.skip_reason, elapsed
        
        try:
            # Resolve fixtures
            fixture_kwargs = self._resolve_fixtures(test_case)
            
            # Call test function
            if test_case.params:
                test_case.func(*test_case.params, **fixture_kwargs)
            else:
                test_case.func(**fixture_kwargs)
            
            elapsed = time.time() - start_time
            return TestStatus.PASSED, "", elapsed
        
        except AssertionError as e:
            elapsed = time.time() - start_time
            return TestStatus.FAILED, str(e), elapsed
        
        except Exception as e:
            elapsed = time.time() - start_time
            return TestStatus.FAILED, f"{type(e).__name__}: {e}", elapsed
        
        finally:
            self._cleanup_fixtures()
    
    def _resolve_fixtures(self, test_case: TestCase) -> Dict[str, Any]:
        """Resolve and set up fixtures needed by test."""
        sig = inspect.signature(test_case.func)
        kwargs = {}
        
        for param_name in sig.parameters:
            if param_name in self.fixtures:
                fixture = self.fixtures[param_name]
                kwargs[param_name] = fixture.setup()
                self.setup_fixtures[param_name] = fixture
        
        return kwargs
    
    def _cleanup_fixtures(self):
        """Clean up fixtures."""
        for fixture in self.setup_fixtures.values():
            fixture.teardown()
        self.setup_fixtures.clear()


class TestRunner:
    """Runs tests with optional parallelization."""
    
    def __init__(self, num_workers: int = 1, verbose: bool = False):
        self.num_workers = num_workers if num_workers > 0 else 1
        self.verbose = verbose
    
    def run_tests(self, tests: List[TestCase], 
                  fixtures: Dict[str, Fixture]) -> TestReport:
        """
        Run all tests and return report.
        
        Args:
            tests: List of test cases to run
            fixtures: Available fixtures
            
        Returns:
            TestReport with all results
        """
        report = TestReport()
        start_time = time.time()
        
        if self.num_workers == 1:
            # Serial execution
            executor = TestExecutor(fixtures)
            for test_case in tests:
                status, error, elapsed = executor.execute(test_case)
                result = TestResult(test_case.get_full_name(), status, elapsed * 1000)
                if error:
                    result.set_error(Exception(error))
                report.add_result(result)
        
        else:
            # Parallel execution
            with Pool(self.num_workers) as pool:
                results = []
                for test_case in tests:
                    # Run in worker process
                    executor = TestExecutor(fixtures)
                    status, error, elapsed = executor.execute(test_case)
                    result = TestResult(test_case.get_full_name(), status, elapsed * 1000)
                    if error:
                        result.set_error(Exception(error))
                    results.append(result)
                    report.add_result(result)
        
        report.total_time_ms = (time.time() - start_time) * 1000
        
        return report


# Test
if __name__ == "__main__":
    print("Testing Test Framework\n")
    
    # Create a simple test
    @test
    def test_sample():
        assert 1 + 1 == 2
    
    # Discover tests (just our sample)
    discoverer = TestDiscoverer("./")
    # Manually add our test
    discoverer.tests.append(TestCase(test_sample, "test_sample", "__main__"))
    
    print(f"Discovered tests: {[t.get_full_name() for t in discoverer.tests]}")
    
    # Run tests
    runner = TestRunner(num_workers=1, verbose=True)
    report = runner.run_tests(discoverer.tests, discoverer.fixtures)
    
    # Print report
    print(report.format_report())
