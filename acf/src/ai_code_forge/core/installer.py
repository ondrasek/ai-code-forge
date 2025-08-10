"""ACF installation logic."""

import shutil
from pathlib import Path
from importlib import resources
import click

class ACFInstaller:
    """Handles ACF configuration installation."""
    
    def __init__(self, target_dir: Path = None):
        """Initialize installer with target directory."""
        self.target_dir = target_dir or Path.cwd()
        self.claude_dir = self.target_dir / ".claude"
        self.acf_dir = self.target_dir / ".acf"
    
    def get_package_data_path(self) -> Path:
        """Get path to bundled package data."""
        # First try development path (when running from source)
        acf_pkg_path = Path(__file__).parent.parent
        data_path = acf_pkg_path / "data"
        if data_path.exists():
            return data_path
        
        # Then try importlib.resources for installed package
        try:
            import ai_code_forge.data
            data_files = resources.files("ai_code_forge.data")
            # For Python 3.9+ with Traversable interface
            if hasattr(data_files, '__fspath__'):
                return Path(data_files.__fspath__())
            else:
                # Handle other resource types
                return Path(str(data_files))
        except Exception as e:
            raise FileNotFoundError(f"Package data not found. Tried:\n1. Development path: {data_path}\n2. Package resources. Error: {e}")
    
    def install(self) -> bool:
        """Install ACF configuration to target directory."""
        try:
            click.echo(f"🚀 Installing ACF configuration to: {self.target_dir}")
            
            # Get package data
            data_path = self.get_package_data_path()
            click.echo(f"📦 Using package data from: {data_path}")
            
            # Create target directories
            self._create_directories()
            
            # Install Claude Code files
            self._install_claude_files(data_path)
            
            # Install ACF files
            self._install_acf_files(data_path)
            
            # Install CLAUDE.md
            self._install_claude_md(data_path)
            
            click.echo("✅ Installation completed successfully!")
            return True
            
        except Exception as e:
            click.echo(f"❌ Installation failed: {e}", err=True)
            return False
    
    def _create_directories(self):
        """Create target directories."""
        click.echo("📁 Creating directories...")
        self.claude_dir.mkdir(exist_ok=True)
        self.acf_dir.mkdir(exist_ok=True)
        click.echo(f"  • Created: {self.claude_dir}")
        click.echo(f"  • Created: {self.acf_dir}")
    
    def _install_claude_files(self, data_path: Path):
        """Install Claude Code recognized files to .claude/"""
        click.echo("🤖 Installing Claude Code files...")
        claude_source = data_path / "claude"
        
        if not claude_source.exists():
            raise FileNotFoundError(f"Claude source not found: {claude_source}")
        
        # Copy all files from claude/ to .claude/
        for item in claude_source.iterdir():
            target = self.claude_dir / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
                click.echo(f"  • Copied directory: {item.name}")
            else:
                shutil.copy2(item, target)
                click.echo(f"  • Copied file: {item.name}")
    
    def _install_acf_files(self, data_path: Path):
        """Install ACF-managed files to .acf/"""
        click.echo("🔧 Installing ACF files...")
        acf_source = data_path / "acf"
        
        if not acf_source.exists():
            raise FileNotFoundError(f"ACF source not found: {acf_source}")
        
        # Copy all files from acf/ to .acf/
        for item in acf_source.iterdir():
            target = self.acf_dir / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
                click.echo(f"  • Copied directory: {item.name}")
            else:
                shutil.copy2(item, target)
                click.echo(f"  • Copied file: {item.name}")
    
    def _install_claude_md(self, data_path: Path):
        """Install CLAUDE.md to project root."""
        click.echo("📄 Installing CLAUDE.md...")
        claude_md_source = data_path / "CLAUDE.md"
        
        if not claude_md_source.exists():
            raise FileNotFoundError(f"CLAUDE.md not found: {claude_md_source}")
        
        claude_md_target = self.target_dir / "CLAUDE.md"
        shutil.copy2(claude_md_source, claude_md_target)
        click.echo(f"  • Installed: CLAUDE.md")
    
    def get_installation_status(self) -> dict:
        """Get current installation status."""
        status = {
            "claude_dir_exists": self.claude_dir.exists(),
            "acf_dir_exists": self.acf_dir.exists(), 
            "claude_md_exists": (self.target_dir / "CLAUDE.md").exists(),
            "claude_files": [],
            "acf_files": []
        }
        
        # Check Claude files
        if status["claude_dir_exists"]:
            status["claude_files"] = [
                f.name for f in self.claude_dir.iterdir()
                if f.is_file() or f.is_dir()
            ]
        
        # Check ACF files  
        if status["acf_dir_exists"]:
            status["acf_files"] = [
                f.name for f in self.acf_dir.iterdir()
                if f.is_file() or f.is_dir()
            ]
        
        return status