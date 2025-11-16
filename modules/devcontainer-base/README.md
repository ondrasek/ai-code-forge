# DevContainer Base Module

Foundation devcontainer infrastructure and setup scripts for AI Code Forge.

## Purpose

This module provides the core devcontainer infrastructure that other language modules build upon:
- Base devcontainer configuration templates
- Comprehensive post-create setup scripts
- Development environment initialization
- Common Docker patterns and utilities

## What's Included

- **DevContainer Templates**: Configurable devcontainer.json and Dockerfile templates
- **Setup Scripts**: Comprehensive post-create environment setup
- **Utility Scripts**: Build, clean, and maintenance utilities
- **Environment Configuration**: SSH, GPG, Git, and shell setup

## Installation

```bash
acforge module install devcontainer-base
```

## Usage

This module is typically used as a dependency by language-specific modules. It provides the foundation that other modules extend with language-specific configurations.

The installed `_devcontainer/` directory contains:
- Template files for customization
- Post-create scripts for environment setup
- Build and maintenance utilities

## Dependencies

None. This is a foundation module.

## Compatibility

- Docker: Required for devcontainer functionality
- Claude Code: >=2.78.0
- AI Code Forge: >=4.0.0

## Notes

This module installs template files that are intended to be customized by language-specific modules or users. The templates use placeholder syntax that should be replaced during module installation.