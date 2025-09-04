#!/usr/bin/env python3
"""Test runner for CLI tests with comprehensive reporting."""

import subprocess
import sys
import time
from pathlib import Path


def run_pytest_with_coverage():
    """Run pytest with coverage reporting."""
    print("🧪 Running Focused AI Code Forge CLI Test Suite")
    print("🎯 9 meaningful tests (no test theater)")
    print("=" * 50)
    
    start_time = time.time()
    
    # Change to CLI directory
    cli_dir = Path(__file__).parent
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/",
        "-v",                           # Verbose output
        "--tb=short",                   # Short traceback format
        "--cov=ai_code_forge_cli",      # Coverage for CLI package
        "--cov-report=term-missing",    # Show missing lines
        "--cov-report=html:htmlcov",    # HTML coverage report
        "--durations=10"                # Show slowest 10 tests
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print(f"Working directory: {cli_dir}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=cli_dir, capture_output=False)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("-" * 50)
        print(f"⏱️  Test execution time: {duration:.2f} seconds")
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            print("📊 Coverage report generated in htmlcov/index.html")
        else:
            print("❌ Some tests failed!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest pytest-cov")
        return False
    
    return True


def run_quick_tests():
    """Run quick tests without coverage for fast feedback."""
    print("⚡ Running Focused Test Suite (No Coverage)")
    print("🎯 9 meaningful tests - no theater")
    print("=" * 50)
    
    cli_dir = Path(__file__).parent
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=line",
        "-x"  # Stop on first failure
    ]
    
    try:
        result = subprocess.run(cmd, cwd=cli_dir)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Quick test execution failed: {e}")
        return False


def main():
    """Main test runner entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CLI tests")
    parser.add_argument("--quick", "-q", action="store_true", 
                       help="Run quick tests without coverage")
    parser.add_argument("--integration-only", "-i", action="store_true",
                       help="Run integration tests only")
    parser.add_argument("--unit-only", "-u", action="store_true", 
                       help="Run unit tests only")
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_tests()
    elif args.integration_only:
        print("🔗 Running Integration Tests Only")
        cmd = [sys.executable, "-m", "pytest", "tests/test_init_integration.py", "-v"]
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        success = result.returncode == 0
    elif args.unit_only:
        print("🔧 Running Unit Tests Only")
        cmd = [sys.executable, "-m", "pytest", "tests/test_parameter_substitution.py", "-v"]
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        success = result.returncode == 0
    else:
        success = run_pytest_with_coverage()
    
    if not success:
        print("\n❌ Test suite failed!")
        sys.exit(1)
    else:
        print("\n✅ Test suite completed successfully!")


if __name__ == "__main__":
    main()