This directory contains TEMPLATES for distribution through modules.

## v4.0+ Modular Architecture

As of v4.0+, templates are distributed through modules rather than atomic deployment:

- **Claude Config**: Moved to `modules/claude-config/` module
- **Devcontainer Templates**: Available as `_devcontainer/` templates
- **Guidelines & Stacks**: Available as templates for modules to reference

## Usage

Templates are no longer deployed directly. Instead:
1. Modules reference templates in their file installations
2. Users install modules which deploy the relevant templates
3. Templates serve as blueprints for module development
