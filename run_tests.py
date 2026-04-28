"""
Python test runner script
Run with: python run_tests.py [option]
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner function."""
    print("=" * 50)
    print("Survey Data Processing Test Runner")
    print("=" * 50)
    print()

    # Check if pytest is available
    try:
        subprocess.run(["pytest", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: pytest is not installed")
        print("Install it with: pip install pytest pytest-cov")
        return 1

    # Parse command line arguments
    option = sys.argv[1] if len(sys.argv) > 1 else "all"

    test_commands = {
        "all": ["pytest", "tests/", "-v"],
        "fish": ["pytest", "tests/test_fish_metrics.py", "-v"],
        "inverts": ["pytest", "tests/test_invert_metrics.py", "-v"],
        "subs": ["pytest", "tests/test_subs_metrics.py", "-v"],
        "integration": ["pytest", "tests/test_integration.py", "-v"],
        "coverage": [
            "pytest",
            "tests/",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term",
        ],
        "quick": ["pytest", "tests/", "-v", "-k", "not integration"],
    }

    if option not in test_commands:
        print(f"Unknown option: {option}")
        print()
        print("Usage: python run_tests.py [option]")
        print()
        print("Options:")
        print("  all         - Run all tests (default)")
        print("  fish        - Run only fish metrics tests")
        print("  inverts     - Run only invertebrate metrics tests")
        print("  subs        - Run only substrate metrics tests")
        print("  integration - Run only integration tests")
        print("  coverage    - Run all tests with coverage report")
        print("  quick       - Run quick tests (excluding integration)")
        return 1

    exit_code = run_command(test_commands[option])

    print()
    if exit_code == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")

    if option == "coverage" and exit_code == 0:
        print()
        print("Coverage report generated in htmlcov/index.html")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
