"""Main CLI entry point."""

import click
from pathlib import Path
from .core.installer import ACFInstaller

@click.group()
@click.version_option(version="0.2.0", package_name="ai-code-forge")
def main():
    """AI Code Forge configuration management tool."""
    pass

@main.command()
@click.option("--target", "-t", type=click.Path(), help="Target directory (default: current directory)")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
def install(target, force):
    """Install AI Code Forge configuration."""
    target_dir = Path(target) if target else Path.cwd()
    
    if not target_dir.exists():
        click.echo(f"❌ Target directory does not exist: {target_dir}", err=True)
        return
    
    # Check if already installed
    installer = ACFInstaller(target_dir)
    status = installer.get_installation_status()
    
    if not force and (status["claude_dir_exists"] or status["acf_dir_exists"]):
        click.echo("⚠️  ACF configuration already exists in target directory")
        click.echo("Use --force to overwrite existing installation")
        click.echo("Run 'ai-code-forge status' to see current installation")
        return
    
    if force:
        click.echo("🔄 Force installation - overwriting existing files")
    
    # Perform installation
    success = installer.install()
    if success:
        click.echo("")
        click.echo("🎉 Ready to use! Your directory now includes:")
        click.echo("  • .claude/ - Claude Code configuration")
        click.echo("  • .acf/ - ACF tools and templates")  
        click.echo("  • CLAUDE.md - Core operational rules")

@main.command()
@click.option("--target", "-t", type=click.Path(), help="Target directory (default: current directory)")
def status(target):
    """Show installation status."""
    target_dir = Path(target) if target else Path.cwd()
    
    installer = ACFInstaller(target_dir)
    status = installer.get_installation_status()
    
    click.echo(f"📊 ACF Installation Status for: {target_dir}")
    click.echo("=" * 50)
    
    # Claude Code files
    if status["claude_dir_exists"]:
        click.echo("✅ Claude Code configuration (.claude/)")
        for file in sorted(status["claude_files"]):
            click.echo(f"  • {file}")
    else:
        click.echo("❌ No Claude Code configuration found")
    
    click.echo("")
    
    # ACF files
    if status["acf_dir_exists"]:
        click.echo("✅ ACF tools and templates (.acf/)")
        for file in sorted(status["acf_files"]):
            click.echo(f"  • {file}")
    else:
        click.echo("❌ No ACF tools found")
    
    click.echo("")
    
    # CLAUDE.md
    if status["claude_md_exists"]:
        click.echo("✅ CLAUDE.md operational rules")
    else:
        click.echo("❌ No CLAUDE.md found")
    
    click.echo("")
    
    # Overall status
    if all([status["claude_dir_exists"], status["acf_dir_exists"], status["claude_md_exists"]]):
        click.echo("🎉 Complete ACF installation detected!")
    elif any([status["claude_dir_exists"], status["acf_dir_exists"], status["claude_md_exists"]]):
        click.echo("⚠️  Partial ACF installation - run 'ai-code-forge install' to complete")
    else:
        click.echo("❌ No ACF installation found - run 'ai-code-forge install' to set up")

if __name__ == "__main__":
    main()