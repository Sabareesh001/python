"""
Test Runner CLI

Command-line interface for running tests.
"""

import sys
import argparse
from pathlib import Path

from framework import TestDiscoverer, TestRunner


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Miniature Test Framework",
        prog="minitest"
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default="./",
        help="Path to test file or directory"
    )
    
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel workers"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Discover tests
    print("=== Test Discovery ===")
    discoverer = TestDiscoverer(args.path)
    tests = discoverer.discover()
    
    print(f"Found {len(tests)} tests")
    if discoverer.fixtures:
        fixtures_list = ", ".join(discoverer.fixtures.keys())
        print(f"Fixtures loaded: {fixtures_list}")
    
    print()
    
    # Run tests
    print("=== Execution ===")
    runner = TestRunner(
        num_workers=args.parallel,
        verbose=args.verbose
    )
    
    report = runner.run_tests(tests, discoverer.fixtures)
    
    # Print report
    print(report.format_report())
    
    # Exit with appropriate code
    summary = report.get_summary()
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
