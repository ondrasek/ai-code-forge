# Publishing Instructions for ai-code-forge Deprecation Package

## Overview

This directory contains a deprecation package for the old `ai-code-forge` PyPI package. When users install or run the old package, they'll receive clear migration instructions to use the new `acforge` package.

## What This Package Does

1. **Shows deprecation warnings** when `ai-code-forge` or `acf` commands are run
2. **Provides migration instructions** with exact commands to switch to `acforge`
3. **Attempts to delegate** to `acforge` if it's already installed
4. **Updates PyPI metadata** to indicate the package is deprecated

## Publishing Steps

### 1. Test Locally First
```bash
cd deprecation-package

# Build the package
python -m build

# Test installation
pip install --force-reinstall dist/ai_code_forge-3.0.0-py3-none-any.whl

# Test commands show deprecation warnings
ai-code-forge --help
acf status
```

### 2. Publish to Test PyPI (Recommended)
```bash
cd deprecation-package

# Install publishing tools if needed
pip install twine

# Upload to test PyPI
twine upload --repository testpypi dist/*

# Test from test PyPI
pip install --index-url https://test.pypi.org/simple/ ai-code-forge
```

### 3. Publish to Production PyPI
```bash
cd deprecation-package

# Upload to production PyPI
twine upload dist/*
```

## Alternative: Using uv
```bash
cd deprecation-package

# Build with uv
uv build

# Publish to test PyPI
uv publish --index-url https://test.pypi.org/legacy/

# Publish to production PyPI  
uv publish
```

## Package Details

- **Version**: 3.0.0 (higher than any existing version)
- **Status**: Development Status :: 7 - Inactive
- **Dependencies**: None (lightweight deprecation notice)
- **Commands**: Both `ai-code-forge` and `acf` show deprecation warnings
- **Fallback**: Attempts to delegate to `acforge` if available

## Expected User Experience

When users run the old commands:

```
$ ai-code-forge --help
⚠️  DEPRECATION WARNING ⚠️

The 'ai-code-forge' package has been renamed to 'acforge'

Please migrate to the new package:
  1. Uninstall this package: uv tool uninstall ai-code-forge
  2. Install new package:    uv tool install acforge
  3. Use new command:        acforge --help

The new 'acforge' command provides the same functionality
with a shorter, more convenient name.

Repository: https://github.com/ondrasek/ai-code-forge
New PyPI:   https://pypi.org/project/acforge/

❌ 'acforge' command not found. Please install it:
   uv tool install acforge
```

## Migration Path

1. **Publish the new `acforge` package first**
2. **Then publish this deprecation package** as ai-code-forge v3.0.0
3. Users installing the old name will get clear migration instructions
4. Users who follow the instructions will get the new package

## Notes

- The deprecation package is intentionally lightweight (no dependencies)
- It uses a high version number (3.0.0) to ensure it's the latest
- PyPI metadata clearly indicates deprecation status
- Links point users to the new package and repository