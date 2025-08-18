# Issue #195: Universal MCP Server Interception and Analysis

## CORRECTED UNDERSTANDING: Universal MCP Interception

The requirement is to intercept and analyze **ANY** MCP server usage - not just bundled MCP servers, but all external/third-party MCP servers that Claude Code may interact with through sub-agents.

### 🎯 Corrected Scope

#### What We Need to Intercept
1. **Any MCP server** configured in `.mcp.json` or `mcp-config.json`
2. **Third-party MCP servers** added by users
3. **External MCP services** that sub-agents may access
4. **Custom MCP implementations** in various languages/frameworks

#### What We Need to Analyze
1. **Which sub-agent** used which MCP server
2. **What MCP tools** were invoked with what parameters
3. **Performance characteristics** of MCP server responses
4. **Success/failure patterns** across different MCP servers
5. **Usage frequency** and patterns over time

## 🏗️ CORRECTED IMPLEMENTATION APPROACH

### Core Challenge: MCP Protocol Interception

The key insight is that we need to intercept at the **MCP protocol level**, not at specific server implementations.

#### MCP Protocol Architecture
```
Claude Code Main Context
    ↓
Sub-Agent (e.g., github-issues-workflow)
    ↓ 
MCP Client (Claude Code's MCP client)
    ↓ [STDIO/HTTP/WebSocket]
External MCP Server (any implementation)
```

**Interception Point**: We need to hook into Claude Code's MCP client layer to capture all outgoing MCP requests and incoming responses, regardless of the target server.

### Implementation Strategy: MCP Client Proxy

#### 1. MCP Client Instrumentation
**Location**: Hook into Claude Code's MCP client implementation

```python
class UniversalMCPInterceptor:
    """Intercepts ALL MCP server communication regardless of server type."""
    
    def __init__(self, original_mcp_client):
        self.original_client = original_mcp_client
        self.analytics_logger = AnalyticsLogger()
        self.active_context = "main"  # Track which agent context is active
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        """Intercept any MCP tool call."""
        start_time = time.time()
        request_id = self._generate_request_id()
        
        # Log the outgoing request
        self.analytics_logger.log_mcp_request({
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "executing_context": self.active_context,  # main or sub-agent name
            "mcp_server": server_name,
            "tool_name": tool_name,
            "sanitized_arguments": self._sanitize_arguments(arguments),
            "argument_types": self._get_argument_types(arguments)
        })
        
        try:
            # Call the actual MCP server
            result = await self.original_client.call_tool(server_name, tool_name, arguments)
            success = True
            error_type = None
            
        except Exception as e:
            result = None
            success = False
            error_type = type(e).__name__
            
        execution_time = (time.time() - start_time) * 1000
        
        # Log the response
        self.analytics_logger.log_mcp_response({
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "executing_context": self.active_context,
            "mcp_server": server_name,
            "tool_name": tool_name,
            "success": success,
            "execution_time_ms": execution_time,
            "error_type": error_type,
            "result_size": len(str(result)) if result else 0,
            "result_type": type(result).__name__ if result else None
        })
        
        return result
    
    def set_executing_context(self, context: str):
        """Set the current executing context (main or sub-agent name)."""
        self.active_context = context
```

#### 2. Context Propagation Through Sub-Agents

**Key Challenge**: Determining which sub-agent is making the MCP call requires sophisticated context propagation.

**Solution**: Implement a context stack that tracks agent execution boundaries:

```python
class SubAgentContextManager:
    """Manages execution context for MCP interception."""
    
    def __init__(self):
        self.context_stack = ["main"]
        self.mcp_interceptor = None
    
    def enter_agent_context(self, agent_name: str):
        """Enter a sub-agent execution context."""
        self.context_stack.append(agent_name)
        if self.mcp_interceptor:
            self.mcp_interceptor.set_executing_context(agent_name)
    
    def exit_agent_context(self):
        """Exit current sub-agent context."""
        if len(self.context_stack) > 1:
            self.context_stack.pop()
        current_context = self.context_stack[-1]
        if self.mcp_interceptor:
            self.mcp_interceptor.set_executing_context(current_context)
    
    @contextmanager
    def agent_execution(self, agent_name: str):
        """Context manager for sub-agent execution."""
        self.enter_agent_context(agent_name)
        try:
            yield
        finally:
            self.exit_agent_context()
```

#### 3. Universal MCP Server Discovery

**Requirement**: Discover and track ALL configured MCP servers regardless of configuration format or location.

**Implementation**: Multi-format configuration parser with fallback detection:

```python
class MCPServerDiscovery:
    """Discovers all configured MCP servers regardless of type."""
    
    def discover_mcp_servers(self) -> Dict[str, Dict]:
        """Find all MCP servers from configuration."""
        servers = {}
        
        # Check standard MCP configuration locations
        config_locations = [
            ".mcp.json",
            "mcp-servers/mcp-config.json",
            ".claude/mcp-servers.json"
        ]
        
        for config_file in config_locations:
            if os.path.exists(config_file):
                with open(config_file) as f:
                    config = json.load(f)
                    
                # Parse different MCP configuration formats
                if "mcpServers" in config:
                    servers.update(self._parse_claude_mcp_config(config["mcpServers"]))
                elif "servers" in config:
                    servers.update(self._parse_generic_mcp_config(config["servers"]))
        
        return servers
    
    def _parse_claude_mcp_config(self, servers_config: Dict) -> Dict[str, Dict]:
        """Parse Claude Code MCP server configuration."""
        discovered = {}
        for server_name, server_config in servers_config.items():
            discovered[server_name] = {
                "type": "claude_mcp",
                "command": server_config.get("command"),
                "args": server_config.get("args", []),
                "env": server_config.get("env", {}),
                "transport": "stdio"  # Default for Claude MCP
            }
        return discovered
    
    def _parse_generic_mcp_config(self, servers_config: Dict) -> Dict[str, Dict]:
        """Parse generic MCP server configuration."""
        discovered = {}
        for server_name, server_config in servers_config.items():
            discovered[server_name] = {
                "type": "generic",
                "endpoint": server_config.get("endpoint"),
                "transport": server_config.get("transport", "http"),
                "auth": server_config.get("auth", {})
            }
        return discovered
```

## Implementation Roadmap

### Phase 1: MCP Client Interception Infrastructure

**Priority**: High - Foundation for all subsequent features

1. **Locate Claude Code's MCP Client Implementation**
   - Find where Claude Code instantiates MCP clients
   - Identify the interface for MCP tool calls
   - Understand the current MCP configuration loading

2. **Implement Universal MCP Interceptor**
   - Create proxy wrapper around existing MCP client
   - Implement request/response logging for ANY MCP server
   - Add context tracking for sub-agent identification

3. **Context Propagation System**
   - Modify Task tool to set agent context before delegation
   - Ensure context is properly cleaned up after agent execution
   - Handle nested agent calls (agent calling another agent)

### Phase 2: Universal MCP Analytics

**Priority**: Medium - Builds on Phase 1 infrastructure

1. **MCP Server Discovery and Cataloging**
   - Scan all MCP configuration files
   - Build registry of available MCP servers
   - Track server types, transports, and capabilities

2. **Protocol-Level Analytics**
   - Track request patterns across ALL MCP servers
   - Monitor performance characteristics by server type
   - Identify usage patterns and bottlenecks

3. **Cross-Server Usage Analysis**
   - Compare usage patterns across different MCP servers
   - Identify which sub-agents prefer which servers
   - Track success rates by server and tool combination

### Phase 3: Advanced Analytics Queries

**Priority**: Medium - Provides actionable insights from collected data

```python
class UniversalMCPAnalytics:
    """Analytics for ANY MCP server usage."""
    
    def get_mcp_server_usage_matrix(self, days: int = 7) -> List[Dict]:
        """Show which sub-agents use which MCP servers."""
        return self.query("""
        SELECT 
            executing_context as agent,
            mcp_server,
            tool_name,
            COUNT(*) as usage_count,
            AVG(execution_time_ms) as avg_response_time,
            success_rate
        FROM mcp_requests mr
        JOIN mcp_responses resp ON mr.request_id = resp.request_id
        WHERE mr.timestamp >= datetime('now', '-{} days')
        GROUP BY executing_context, mcp_server, tool_name
        ORDER BY usage_count DESC
        """.format(days))
    
    def get_mcp_server_performance(self, server_name: str = None) -> List[Dict]:
        """Analyze performance characteristics of MCP servers."""
        server_filter = f"AND mcp_server = '{server_name}'" if server_name else ""
        
        return self.query(f"""
        SELECT 
            mcp_server,
            tool_name,
            COUNT(*) as total_calls,
            AVG(execution_time_ms) as avg_time,
            MIN(execution_time_ms) as min_time,
            MAX(execution_time_ms) as max_time,
            PERCENTILE_90(execution_time_ms) as p90_time,
            (SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
        FROM mcp_responses
        WHERE timestamp >= datetime('now', '-7 days') {server_filter}
        GROUP BY mcp_server, tool_name
        ORDER BY total_calls DESC
        """)
    
    def get_cross_server_usage_patterns(self) -> List[Dict]:
        """Identify patterns of MCP server usage across sub-agents."""
        return self.query("""
        WITH agent_server_usage AS (
            SELECT 
                executing_context,
                mcp_server,
                COUNT(*) as usage_count
            FROM mcp_requests
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY executing_context, mcp_server
        )
        SELECT 
            executing_context,
            GROUP_CONCAT(mcp_server || ':' || usage_count) as server_usage_pattern,
            COUNT(DISTINCT mcp_server) as unique_servers_used
        FROM agent_server_usage
        GROUP BY executing_context
        ORDER BY unique_servers_used DESC
        """)
```

### Data Schema for Universal MCP Analytics

```sql
-- MCP Requests (any server)
CREATE TABLE mcp_requests (
    request_id TEXT PRIMARY KEY,
    timestamp TEXT,
    session_id TEXT,
    executing_context TEXT,  -- 'main' or sub-agent name
    mcp_server TEXT,         -- server name from config
    tool_name TEXT,
    sanitized_arguments TEXT, -- JSON
    argument_types TEXT       -- JSON
);

-- MCP Responses (any server)  
CREATE TABLE mcp_responses (
    request_id TEXT,
    timestamp TEXT,
    mcp_server TEXT,
    tool_name TEXT,
    success BOOLEAN,
    execution_time_ms REAL,
    error_type TEXT,
    result_size INTEGER,
    result_type TEXT,
    FOREIGN KEY (request_id) REFERENCES mcp_requests(request_id)
);

-- MCP Server Registry
CREATE TABLE mcp_servers (
    server_name TEXT PRIMARY KEY,
    server_type TEXT,        -- 'claude_mcp', 'generic', 'custom'
    transport TEXT,          -- 'stdio', 'http', 'websocket'
    endpoint TEXT,           -- for HTTP/WebSocket servers
    command TEXT,            -- for STDIO servers
    discovery_timestamp TEXT,
    last_seen TEXT
);
```

### CLI Commands for Universal MCP Analysis

```bash
# Analyze ANY MCP server usage by sub-agents
acf analytics mcp-usage --days 7

# Performance analysis for specific MCP server
acf analytics mcp-performance --server github-mcp

# Cross-server usage patterns
acf analytics mcp-patterns

# Discover all configured MCP servers
acf analytics mcp-discovery
```

## 🎯 Key Implementation Questions

1. **MCP Client Location**: Where exactly does Claude Code instantiate its MCP clients? We need to hook at the right architectural level.

2. **Agent Context Boundaries**: How can we reliably detect when execution moves from main context to a sub-agent and back?

3. **MCP Configuration Discovery**: What are all the possible locations and formats for MCP server configurations that Claude Code supports?

4. **Protocol Support**: Does Claude Code support different MCP transports (STDIO, HTTP, WebSocket) that we need to intercept differently?

5. **Performance Impact**: What's the acceptable overhead for intercepting every MCP call across all servers?

This universal interception approach will give you complete visibility into how any sub-agent uses any MCP server, regardless of implementation or origin.

## Next Steps

This universal interception approach provides the foundation for comprehensive MCP analytics across any server implementation. The key technical challenges are:

1. **Architecture Integration**: Hooking into Claude Code's MCP client layer
2. **Context Propagation**: Reliable sub-agent identification 
3. **Performance Optimization**: Minimal overhead for production use
4. **Universal Compatibility**: Support for all MCP transport protocols

Implementation should begin with Phase 1 (MCP Client Interception Infrastructure) as it establishes the foundation for all subsequent analytics capabilities.