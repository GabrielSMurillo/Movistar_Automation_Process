#!/usr/bin/env python3
"""
Test runner for Movistar system.

Runs all tests and generates coverage report.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Verbose
    python run_tests.py --cov        # With coverage
    python run_tests.py --quick      # Quick tests only
"""

import sys
import subprocess
from pathlib import Path

def run_tests(args=None):
    """Run pytest with specified arguments."""
    if args is None:
        args = sys.argv[1:]
    
    # Base pytest command
    pytest_args = ['pytest', 'tests/']
    
    # Add verbosity
    if '-v' not in args and '--verbose' not in args:
        pytest_args.append('-v')
    
    # Add coverage if requested
    if '--cov' in args or '--coverage' in args:
        pytest_args.extend([
            '--cov=src',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
        args = [a for a in args if a not in ['--cov', '--coverage']]
    
    # Quick mode (only fast tests)
    if '--quick' in args:
        pytest_args.extend(['-m', 'not slow'])
        args = [a for a in args if a != '--quick']
    
    # Add remaining args
    pytest_args.extend(args)
    
    print("=" * 80)
    print("[EMOJI] RUNNING MOVISTAR SYSTEM TESTS")
    print("=" * 80)
    print(f"Command: {' '.join(pytest_args)}")
    print("=" * 80)
    
    # Run tests
    result = subprocess.run(pytest_args)
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(run_tests())
