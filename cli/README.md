# AI Code Forge

Configuration management tool for AI Code Forge - automated deployment of Claude Code configurations, templates, and development tools.

## Installation

```bash
pip install ai-code-forge
```

## Usage

### Install Configuration

Deploy complete AI Code Forge configuration to your project:

```bash
acf install
```

Options:
- `--target PATH` - Install to specific directory (default: current directory)
- `--force` - Overwrite existing files

### Check Status

Verify your AI Code Forge installation:

```bash
acf status
```

## What Gets Installed

- **`.claude/`** - Claude Code agents, commands, and settings
- **`.acf/`** - Templates, documentation, and scripts
- **`CLAUDE.md`** - Core operational rules and guidelines

## Requirements

- Python 3.13+
- Claude Code CLI

## Project

This tool is part of the [AI Code Forge](https://github.com/ondrasek/ai-code-forge) project - a comprehensive template system that enhances Claude Code with specialized AI agents, technology stack configurations, and automated workflows.