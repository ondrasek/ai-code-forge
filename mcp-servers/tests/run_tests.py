#!/usr/bin/env python3
"""
Comprehensive test runner for AI Code Forge MCP servers.

This script runs all test categories with proper error handling and reporting.
Supports different test environments and provides detailed output.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Tuple
import time


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class TestRunner:
    """Comprehensive test runner for MCP servers."""
    
    def __init__(self, verbose: bool = False, environment: str = "local"):
        self.verbose = verbose
        self.environment = environment
        self.mcp_servers_dir = Path(__file__).parent.parent
        self.failed_suites = []
        self.total_start_time = time.time()
        
    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
    def print_section(self, text: str) -> None:
        """Print a formatted section header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'▶ ' + text}{Colors.RESET}")
        print(f"{Colors.BLUE}{'-' * (len(text) + 2)}{Colors.RESET}")
        
    def print_success(self, text: str) -> None:
        """Print success message."""
        print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")
        
    def print_error(self, text: str) -> None:
        """Print error message."""
        print(f"{Colors.RED}❌ {text}{Colors.RESET}")
        
    def print_warning(self, text: str) -> None:
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")
        
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        self.print_section("Checking Dependencies")
        
        # Check if we're in the right directory
        if not (self.mcp_servers_dir / "tests").exists():
            self.print_error("Not running from mcp-servers/tests/ directory")
            return False
            
        # Check for pytest
        try:
            result = subprocess.run(["python", "-m", "pytest", "--version"], 
                                  capture_output=True, text=True, cwd=self.mcp_servers_dir)
            if result.returncode == 0:
                self.print_success(f"pytest available: {result.stdout.strip()}")
            else:
                self.print_error("pytest not available")
                return False
        except FileNotFoundError:
            self.print_error("Python not found")
            return False
            
        # Check for required packages
        required_packages = ["psutil", "pydantic", "httpx"]
        for package in required_packages:
            try:
                result = subprocess.run(["python", "-c", f"import {package}"], 
                                      capture_output=True, cwd=self.mcp_servers_dir)
                if result.returncode == 0:
                    self.print_success(f"{package} available")
                else:
                    self.print_warning(f"{package} may not be available")
            except Exception as e:
                self.print_warning(f"Could not check {package}: {e}")
                
        return True
        
    def run_command(self, cmd: List[str], description: str, cwd: Optional[Path] = None) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        if cwd is None:
            cwd = self.mcp_servers_dir
            
        start_time = time.time()
        
        try:
            env = os.environ.copy()
            env["PERFORMANCE_TEST_ENV"] = self.environment
            # Set PYTHONPATH to include mcp-servers directory for tests.shared module
            env["PYTHONPATH"] = str(self.mcp_servers_dir)
            
            # Set logging environment variables to disable logging in CI
            if self.environment == "ci":
                env["PERPLEXITY_LOG_LEVEL"] = "none"
                env["OPENAI_STRUCTURED_LOG_LEVEL"] = "none"
            else:
                # For non-CI environments, set up minimal logging paths
                log_dir = self.mcp_servers_dir / "logs"
                log_dir.mkdir(exist_ok=True)
                env["PERPLEXITY_LOG_PATH"] = str(log_dir / "perplexity.log")
                env["OPENAI_STRUCTURED_LOG_PATH"] = str(log_dir / "openai.log")
            
            if self.verbose:
                print(f"Running: {' '.join(cmd)}")
                print(f"Working directory: {cwd}")
                print(f"Environment: PERFORMANCE_TEST_ENV={self.environment}")
                
            result = subprocess.run(
                cmd, 
                cwd=cwd,
                capture_output=not self.verbose,
                text=True,
                env=env
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.print_success(f"{description} passed ({duration:.1f}s)")
                return True, result.stdout if result.stdout else ""
            else:
                self.print_error(f"{description} failed ({duration:.1f}s)")
                if not self.verbose and result.stderr:
                    print(f"{Colors.RED}{result.stderr}{Colors.RESET}")
                return False, result.stderr if result.stderr else ""
                
        except Exception as e:
            self.print_error(f"{description} failed with exception: {e}")
            return False, str(e)
            
    def run_test_suite(self, test_path: str, description: str, extra_args: List[str] = None) -> bool:
        """Run a specific test suite."""
        cmd = ["python", "-m", "pytest", test_path]
        if extra_args:
            cmd.extend(extra_args)
        if self.verbose:
            cmd.append("-v")
        else:
            cmd.extend(["-q", "--tb=short"])
            
        success, output = self.run_command(cmd, description)
        if not success:
            self.failed_suites.append(description)
        return success
        
    def run_all_tests(self, include_slow: bool = False) -> bool:
        """Run all test suites."""
        all_passed = True
        
        # 1. Shared utilities tests (if any unit tests exist)
        self.print_section("Shared Utilities")
        shared_tests_dir = self.mcp_servers_dir / "tests" / "shared"
        if any(shared_tests_dir.glob("test_*.py")):
            success = self.run_test_suite("tests/shared/", "Shared utilities tests")
            all_passed = all_passed and success
        else:
            self.print_warning("No shared utility tests found")
            
        # 2. Individual MCP server tests
        self.print_section("Individual MCP Server Tests")
        
        # Perplexity MCP tests
        perplexity_tests = self.mcp_servers_dir / "perplexity-mcp" / "tests"
        if perplexity_tests.exists():
            success = self.run_test_suite("perplexity-mcp/tests/", "Perplexity MCP server tests")
            all_passed = all_passed and success
        else:
            self.print_warning("Perplexity MCP tests not found")
            
        # OpenAI MCP tests  
        openai_tests = self.mcp_servers_dir / "openai-structured-mcp" / "tests"
        if openai_tests.exists():
            success = self.run_test_suite("openai-structured-mcp/tests/", "OpenAI structured MCP server tests")
            all_passed = all_passed and success
        else:
            self.print_warning("OpenAI MCP tests not found")
            
        # 3. Cross-server integration tests
        self.print_section("Cross-Server Integration Tests")
        
        # Performance baselines
        success = self.run_test_suite("tests/benchmark/", "Performance baseline tests")
        all_passed = all_passed and success
        
        # Integration workflows
        success = self.run_test_suite("tests/integration/", "Integration workflow tests")
        all_passed = all_passed and success
        
        # Validation tests
        validation_dir = self.mcp_servers_dir / "tests" / "validation"
        if validation_dir.exists() and any(validation_dir.glob("test_*.py")):
            success = self.run_test_suite("tests/validation/", "Validation tests")
            all_passed = all_passed and success
            
        # 4. Load tests (optional, resource intensive)
        if include_slow:
            self.print_section("Load Tests (Resource Intensive)")
            self.print_warning("Running load tests - this may take several minutes")
            success = self.run_test_suite("tests/load/", "Load and stress tests", ["-s"])
            all_passed = all_passed and success
        else:
            self.print_warning("Skipping load tests (use --include-slow to run them)")
            
        return all_passed
        
    def run_coverage_report(self) -> bool:
        """Generate coverage report."""
        self.print_section("Coverage Report")
        
        cmd = [
            "python", "-m", "pytest", 
            "--cov=perplexity_mcp",
            "--cov=openai_structured_mcp", 
            "--cov=tests.shared",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "tests/",
            "perplexity-mcp/tests/",
            "openai-structured-mcp/tests/"
        ]
        
        success, output = self.run_command(cmd, "Coverage analysis")
        if success:
            self.print_success("Coverage report generated in htmlcov/")
        return success
        
    def print_summary(self) -> None:
        """Print test run summary."""
        total_duration = time.time() - self.total_start_time
        
        self.print_header("Test Run Summary")
        
        print(f"{Colors.BOLD}Environment:{Colors.RESET} {self.environment}")
        print(f"{Colors.BOLD}Total Duration:{Colors.RESET} {total_duration:.1f} seconds")
        print(f"{Colors.BOLD}Working Directory:{Colors.RESET} {self.mcp_servers_dir}")
        
        if self.failed_suites:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Test Suites:{Colors.RESET}")
            for suite in self.failed_suites:
                print(f"  {Colors.RED}• {suite}{Colors.RESET}")
            print(f"\n{Colors.RED}{Colors.BOLD}Overall Result: FAILED{Colors.RESET}")
            return False
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}Overall Result: ALL TESTS PASSED ✅{Colors.RESET}")
            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for AI Code Forge MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                     # Run all tests (local environment)
  python run_tests.py --verbose           # Run with detailed output
  python run_tests.py --env ci            # Run with CI environment baselines
  python run_tests.py --include-slow      # Include resource-intensive load tests
  python run_tests.py --coverage          # Generate coverage report
  python run_tests.py --quick             # Run only fast tests (no integration)
        """
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--environment", "--env",
        choices=["local", "ci", "production"],
        default="local",
        help="Test environment (affects performance baselines)"
    )
    
    parser.add_argument(
        "--include-slow",
        action="store_true", 
        help="Include resource-intensive load tests"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only fast unit tests (skip integration and load tests)"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose, environment=args.environment)
    
    runner.print_header("AI Code Forge MCP Server Test Suite")
    
    # Check dependencies
    if not runner.check_dependencies():
        sys.exit(1)
        
    # Run tests
    if args.quick:
        runner.print_section("Quick Test Mode - Unit Tests Only")
        success = True
        success &= runner.run_test_suite("perplexity-mcp/tests/test_client.py", "Perplexity client tests")
        success &= runner.run_test_suite("perplexity-mcp/tests/test_server.py", "Perplexity server tests") 
        success &= runner.run_test_suite("openai-structured-mcp/tests/test_client.py", "OpenAI client tests")
        success &= runner.run_test_suite("openai-structured-mcp/tests/test_server.py", "OpenAI server tests")
    else:
        success = runner.run_all_tests(include_slow=args.include_slow)
        
    # Generate coverage report if requested
    if args.coverage and success:
        runner.run_coverage_report()
        
    # Print summary
    final_success = runner.print_summary()
    
    sys.exit(0 if final_success else 1)


if __name__ == "__main__":
    main()