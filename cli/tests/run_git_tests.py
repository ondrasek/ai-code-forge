#!/usr/bin/env python3
"""Test runner for git integration tests."""

import subprocess
import sys
from pathlib import Path


def run_git_tests():
    """Run all git integration tests with appropriate configuration."""
    
    # Set up environment
    cli_root = Path(__file__).parent.parent
    src_path = cli_root / "src"
    
    env = {"PYTHONPATH": str(src_path)}
    
    print("🧪 Running Git Integration Test Suite")
    print("=" * 50)
    
    test_suites = [
        ("Unit Tests", "tests/test_git_integration_unit.py"),
        ("End-to-End Tests", "tests/test_git_integration_e2e.py"),
    ]
    
    overall_success = True
    
    for suite_name, test_file in test_suites:
        print(f"\n📋 {suite_name}")
        print("-" * 30)
        
        cmd = [
            sys.executable, "-m", "pytest", 
            test_file,
            "-v",
            "--tb=short",
            "--color=yes"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cli_root,
                env={**subprocess.os.environ, **env},
                check=True
            )
            print(f"✅ {suite_name} PASSED")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {suite_name} FAILED (exit code: {e.returncode})")
            overall_success = False
        except Exception as e:
            print(f"💥 {suite_name} ERROR: {e}")
            overall_success = False
    
    print("\n" + "=" * 50)
    
    if overall_success:
        print("🎉 ALL GIT INTEGRATION TESTS PASSED!")
        return 0
    else:
        print("💔 SOME GIT INTEGRATION TESTS FAILED!")
        return 1


def run_quick_smoke_test():
    """Run a quick smoke test to verify git integration basics."""
    
    cli_root = Path(__file__).parent.parent
    src_path = cli_root / "src"
    
    env = {"PYTHONPATH": str(src_path)}
    
    print("🚀 Running Git Integration Smoke Test")
    print("=" * 40)
    
    # Quick tests that should pass fast
    smoke_tests = [
        "tests/test_git_integration_unit.py::TestGitCommandWrapper::test_generate_commit_message_initial",
        "tests/test_git_integration_unit.py::TestGitCommandWrapper::test_acf_file_patterns",
        "tests/test_git_integration_e2e.py::TestGitIntegrationE2E::test_init_without_git_no_commit"
    ]
    
    for test in smoke_tests:
        cmd = [sys.executable, "-m", "pytest", test, "-v", "--tb=line"]
        
        try:
            subprocess.run(
                cmd,
                cwd=cli_root,
                env={**subprocess.os.environ, **env},
                check=True,
                capture_output=True
            )
            print(f"✅ {test.split('::')[-1]}")
            
        except subprocess.CalledProcessError:
            print(f"❌ {test.split('::')[-1]}")
            return 1
    
    print("\n🎉 Git integration smoke test PASSED!")
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run git integration tests")
    parser.add_argument(
        "--smoke", 
        action="store_true", 
        help="Run quick smoke test only"
    )
    
    args = parser.parse_args()
    
    if args.smoke:
        sys.exit(run_quick_smoke_test())
    else:
        sys.exit(run_git_tests())