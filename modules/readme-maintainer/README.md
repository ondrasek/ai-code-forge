# README Maintainer Module

README template generation and maintenance for AI Code Forge projects.

## Purpose

This module provides static README templates for different project types:
- General project documentation structure
- Library and package documentation patterns
- MCP server documentation templates
- Standardized documentation sections

## What's Included

- **Project Templates**: General purpose project README templates
- **Library Templates**: Package and library documentation patterns
- **Specialized Templates**: MCP server and specific project type templates
- **Documentation Standards**: Consistent structure and sections

## Installation

```bash
acforge module install readme-maintainer
```

## Usage

After installation, README templates are available in `readme/`:

```bash
# Copy template for new project
cp readme/general-project-template.md README.md

# Use library template for packages
cp readme/library-package-template.md README.md

# Use MCP server template
cp readme/mcp-server-template.md README.md
```

## Templates Available

- `general-project-template.md` - Standard project documentation
- `library-package-template.md` - Library and package projects
- `mcp-server-template.md` - MCP server documentation

## Dependencies

None. This module provides static templates.

## Compatibility

- Claude Code: >=2.78.0
- AI Code Forge: >=4.0.0

## Notes

This module provides static templates that complement skills-based README generation. Templates serve as fallbacks and starting points for documentation creation.