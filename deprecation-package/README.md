# ⚠️ DEPRECATED: ai-code-forge

**This package has been renamed to `acforge` for better usability.**

## Migration Instructions

### For new installations:
```bash
# Install the new package
uv tool install acforge

# Use the new command
acforge --help
```

### For existing users:
```bash
# Uninstall the old package
uv tool uninstall ai-code-forge

# Install the new package  
uv tool install acforge

# Update your scripts to use 'acforge' instead of 'acf' or 'ai-code-forge'
```

## What Changed

- **Package name**: `ai-code-forge` → `acforge`
- **Command name**: `acf` / `ai-code-forge` → `acforge`
- **Installation**: `uvx ai-code-forge` → `uvx acforge`

## Why the Change?

The new `acforge` name is:
- Shorter and easier to type
- Available on PyPI (ai-code-forge conflicts were resolved)
- More consistent branding

## New Package Details

- **PyPI**: https://pypi.org/project/acforge/
- **Repository**: https://github.com/ondrasek/ai-code-forge
- **Documentation**: Same location, updated for new command name

---

**This deprecation package will display warnings when used and redirect you to install `acforge`.**