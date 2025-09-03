"""Pytest configuration for MCP server integration tests."""

import sys
from pathlib import Path

# Add mcp-servers directory to Python path for shared imports
mcp_servers_root = Path(__file__).parent.parent
if str(mcp_servers_root) not in sys.path:
    sys.path.insert(0, str(mcp_servers_root))

# Add individual server source directories to Python path
perplexity_src = mcp_servers_root / "perplexity-mcp" / "src"
openai_src = mcp_servers_root / "openai-structured-mcp" / "src"

for src_path in [perplexity_src, openai_src]:
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))