"""Main CLI entry point for AI Code Forge."""

from pathlib import Path
from typing import Optional

import click

from . import __version__
from .commands.init import init_command
from .commands.status import status_command
from .commands.update import update_command


class ACFContext:
    """Shared CLI context object."""
    
    def __init__(self) -> None:
        """Initialize CLI context."""
        self.repo_root: Optional[Path] = None
        self.verbose: bool = False
        self.git: bool = False
    
    def find_repo_root(self) -> Path:
        """Find repository root directory.
        
        Returns:
            Path to repository root
            
        Raises:
            click.ClickException: If repository root cannot be found
        """
        if self.repo_root is not None:
            return self.repo_root
        
        current = Path.cwd()
        
        # Look for .git directory or existing .acforge/.claude directories
        for path in [current] + list(current.parents):
            if any((path / marker).exists() for marker in [".git", ".acforge", ".claude"]):
                self.repo_root = path
                return path
        
        # Default to current directory if no markers found
        self.repo_root = current
        return current


pass_context = click.make_pass_decorator(ACFContext, ensure=True)


@click.group(invoke_without_command=True)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--repo-root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Repository root directory (auto-detected if not specified)"
)
@click.option(
    "--git",
    is_flag=True,
    help="Automatically commit changes to git with version-based commit messages"
)
@click.version_option(version=__version__, prog_name="acforge")
@click.pass_context
def main(ctx: click.Context, verbose: bool, repo_root: Optional[Path], git: bool) -> None:
    """AI Code Forge CLI - Template management for AI development workflows.
    
    The ACF CLI helps manage AI development configurations including:
    - Claude Code agent configurations
    - Development workflow templates
    - Project structure templates
    - Custom command definitions
    
    Use 'acforge COMMAND --help' for detailed help on specific commands.
    """
    # Initialize shared context
    acf_ctx = ACFContext()
    acf_ctx.verbose = verbose
    acf_ctx.git = git
    if repo_root:
        acf_ctx.repo_root = repo_root
    
    ctx.obj = acf_ctx
    
    # If no command specified, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Add commands
main.add_command(init_command)
main.add_command(status_command)
main.add_command(update_command)


if __name__ == "__main__":
    main()