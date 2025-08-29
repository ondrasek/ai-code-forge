#!/usr/bin/env python3
"""Main entry point for deprecated ai-code-forge package."""

import sys
import subprocess
from typing import NoReturn


def main() -> NoReturn:
    """Show deprecation warning and suggest migration to acforge."""
    print("⚠️  DEPRECATION WARNING ⚠️")
    print()
    print("The 'ai-code-forge' package has been renamed to 'acforge'")
    print()
    print("Please migrate to the new package:")
    print("  1. Uninstall this package: uv tool uninstall ai-code-forge")
    print("  2. Install new package:    uv tool install acforge") 
    print("  3. Use new command:        acforge --help")
    print()
    print("The new 'acforge' command provides the same functionality")
    print("with a shorter, more convenient name.")
    print()
    print("Repository: https://github.com/ondrasek/ai-code-forge")
    print("New PyPI:   https://pypi.org/project/acforge/")
    print()
    
    # Try to detect if acforge is already available
    try:
        result = subprocess.run(
            ["acforge"] + sys.argv[1:], 
            check=False,
            capture_output=False
        )
        print("✅ Successfully delegated to 'acforge' command")
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ 'acforge' command not found. Please install it:")
        print("   uv tool install acforge")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()