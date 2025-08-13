# OpenAI Codex CLI MCP Server Setup

## 🚀 **Native MCP Integration**

OpenAI Codex CLI now supports **native MCP protocol** via stdio transport. This document covers setup and configuration for direct integration with Claude Code.

## 📋 **Prerequisites**

### **1. Install OpenAI Codex CLI**

**Option A: NPM (Recommended)**
```bash
npm install -g @openai/codex
```

**Option B: Homebrew (macOS)**
```bash
brew install codex
```

**Option C: Direct Download**
```bash
# Download from GitHub releases
curl -L https://github.com/openai/codex/releases/latest/download/codex-linux -o codex
chmod +x codex
sudo mv codex /usr/local/bin/
```

### **2. System Requirements**
- **Node.js**: 22+ (for npm installation)
- **OS**: macOS 12+, Ubuntu 20.04+, Windows 11 (WSL2 only)
- **RAM**: 4GB minimum, 8GB recommended
- **Network**: Internet access for OpenAI API

### **3. Authentication Setup**

**Option A: ChatGPT Account (Preferred)**
```bash
# Interactive login with ChatGPT Plus/Pro/Team account
codex auth login
```

**Option B: API Key**
```bash
# Set environment variable
export OPENAI_API_KEY="your-openai-api-key"
```

## ⚙️ **MCP Configuration**

The MCP server is pre-configured in `mcp-config.json`:

```json
{
  "mcpServers": {
    "openai-codex": {
      "command": "codex",
      "args": ["mcp"],
      "env": {
        "OPENAI_API_KEY": ""
      },
      "disabled": false,
      "alwaysAllow": ["*"],
      "description": "Native OpenAI Codex CLI MCP server (experimental)"
    }
  }
}
```

## 🧪 **Verification**

### **1. Test Codex CLI Installation**
```bash
# Verify installation
codex --version

# Test basic functionality
codex "Generate a hello world function in Python"
```

### **2. Test MCP Mode**
```bash
# Launch MCP server directly
codex mcp

# Should output MCP initialization messages
```

### **3. Test Claude Code Integration**
1. Start Claude Code with MCP servers enabled
2. Verify `openai-codex` server is connected
3. Test Codex tools in conversation

## ⚠️ **Important Notes**

### **Experimental Status**
- **Current Status**: `codex mcp` is marked as **experimental**
- **Limitations**: Single tool functionality vs. full CLI capabilities  
- **Stability**: May change in future CLI updates
- **Documentation**: Limited official guidance available

### **Alternative Configuration**
For production stability, consider using the **enhanced `openai-structured` server** which includes Codex-style tools via stable OpenAI API:

```json
"openai-structured": {
  "command": "uv",
  "args": ["run", "--directory", "mcp-servers/openai-structured-mcp", "openai-structured-mcp"],
  "env": {
    "OPENAI_API_KEY": "",
    "MCP_LOG_LEVEL": "info"
  },
  "disabled": false,
  "description": "Stable Codex-style tools via OpenAI API"
}
```

## 🔧 **Troubleshooting**

### **Common Issues**

**❌ `codex: command not found`**
```bash
# Verify installation path
which codex
npm list -g @openai/codex

# Add to PATH if necessary
export PATH="$PATH:$(npm root -g)/@openai/codex/bin"
```

**❌ `mcp: unknown command`**
```bash
# Update to latest version
npm update -g @openai/codex

# Verify MCP support
codex --help | grep mcp
```

**❌ Authentication failures**
```bash
# Re-authenticate
codex auth logout
codex auth login

# Or set API key
export OPENAI_API_KEY="your-key"
```

**❌ MCP connection issues**
```bash
# Enable debug logging
export DEBUG="codex:mcp"
codex mcp
```

### **Performance Optimization**

**Memory Usage**
```bash
# Monitor memory usage
codex mcp --memory-limit 2048  # 2GB limit
```

**Request Timeout**
```bash
# Adjust timeout for slow connections
export CODEX_TIMEOUT=60000  # 60 seconds
```

## 🔄 **Migration Guide**

### **From Custom Implementation**
If migrating from a custom Codex wrapper:

1. **Disable custom server** in `mcp-config.json`
2. **Enable native server** with `"openai-codex"`  
3. **Test functionality** matches previous implementation
4. **Update documentation** and workflows

### **Fallback Strategy**
Keep both configurations available:

```json
{
  "mcpServers": {
    "openai-codex": {
      "disabled": false,
      "description": "Native Codex CLI (experimental)"
    },
    "openai-structured": {
      "disabled": true,
      "description": "Fallback Codex-style tools (stable)"
    }
  }
}
```

Switch between them by toggling the `disabled` flag.

## 📊 **Feature Comparison**

| **Feature** | **Native MCP** | **Structured Server** |
|-------------|----------------|----------------------|
| **Stability** | Experimental | Production-ready |
| **Performance** | Variable | Consistent 50-100ms |
| **Tool Count** | Limited | 4 comprehensive tools |
| **Error Handling** | Basic | Advanced with retry logic |
| **Documentation** | Minimal | Complete |
| **Authentication** | CLI-based | Environment variables |

## 🚀 **Getting Started**

1. **Install**: `npm install -g @openai/codex`
2. **Authenticate**: `codex auth login`  
3. **Test**: `codex mcp`
4. **Integrate**: Use pre-configured `mcp-config.json`
5. **Verify**: Test in Claude Code session

The native OpenAI Codex CLI MCP integration is now ready for use! 🎉

---

**Note**: Monitor OpenAI announcements for changes to experimental MCP support and plan migration strategies accordingly.