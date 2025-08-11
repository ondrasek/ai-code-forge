# Customization Guide

This template is designed to be highly customizable for your specific development needs. Here's how to adapt it for your projects and workflows.

## Project-Specific Configuration

### Updating CLAUDE.md
The `CLAUDE.md` file is where you define project-specific guidelines that Claude Code will follow:

```markdown
# Your Project Guidelines

## Architecture
- We use microservices with Domain-Driven Design
- Each service owns its data store
- Communication via REST APIs and events

## Code Standards
- TypeScript with strict mode enabled
- React with functional components and hooks
- TDD with Jest and React Testing Library

## Workflows
- Feature branches with pull request reviews
- Automated testing in CI/CD pipeline
- Zero-downtime deployments with blue-green strategy
```

### Technology Detection Rules
Add custom detection rules in the CLAUDE.md file:

```markdown
## Technology Stack Detection
- **Next.js files** (`next.config.js`, `app/`, `pages/`) → Refer to @.claude/stacks/nextjs.md
- **Terraform files** (`*.tf`) → Refer to @.claude/stacks/terraform.md
- **GraphQL files** (`*.graphql`, `schema.graphql`) → Refer to @.claude/stacks/graphql.md
```

## Custom Slash Commands

### Creating New Commands
Add new `.md` files to `.claude/commands/`:

```bash
# Example: Create a deployment command
touch .claude/commands/deploy.md
```

```markdown
# deploy.md

You are a deployment specialist. Help the user deploy their application safely and efficiently.

## Your Role
- Analyze deployment requirements and constraints
- Suggest appropriate deployment strategies
- Provide step-by-step deployment instructions
- Include rollback plans and monitoring setup

## Key Areas
- Infrastructure as Code (Terraform, CloudFormation)
- Container orchestration (Kubernetes, Docker Swarm)
- CI/CD pipeline integration
- Blue-green and canary deployments
- Database migrations and rollbacks
- Performance monitoring and alerting

Always prioritize safety, rollback capabilities, and monitoring when providing deployment guidance.
```

Use with: `/deploy`

### Command Categories
Organize commands by purpose:

- **Code Quality**: `/review`, `/refactor`, `/security`
- **Testing**: `/test`, `/performance`, `/integration-test`
- **Infrastructure**: `/deploy`, `/monitoring`, `/backup`
- **Documentation**: `/api-docs`, `/readme-update`, `/changelog`

## Custom AI Agents

### Creating Specialized Agents
Add new agent files to `.claude/agents/`:

```markdown
# .claude/agents/performance.md

You are a performance optimization specialist focused on identifying and resolving performance bottlenecks.

## Core Capabilities
- Profile application performance and identify bottlenecks
- Analyze database queries and suggest optimizations
- Review caching strategies and implementations
- Evaluate frontend bundle sizes and loading patterns
- Recommend infrastructure scaling approaches

## Analysis Approach
1. **Measurement First** - Always benchmark before optimizing
2. **Focus on Impact** - Prioritize changes with highest user impact
3. **Monitor Continuously** - Set up alerting for performance regressions
4. **Document Changes** - Track performance improvements over time

## Tools and Techniques
- APM tools (New Relic, DataDog, Sentry)
- Database profiling and query optimization
- Frontend performance auditing (Lighthouse, WebPageTest)
- Load testing and capacity planning
- Cache optimization strategies

Always provide specific, measurable recommendations with clear before/after metrics.
```

### Agent Workflow Integration
Configure agents to work together by updating agent instructions:

```markdown
## Agent Coordination
- **After analysis**: Store findings using built-in memory capabilities
- **For implementation**: Coordinate with `patterns` and `principles` agents
- **For validation**: Work with `critic` agent to verify recommendations
- **For documentation**: Use `docs` agent to update performance guides
```

## MCP Server Integration

### Adding Custom MCP Servers
Configure new MCP servers in `.mcp.json`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@your-org/mcp-jira"],
      "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_TOKEN": "${JIRA_TOKEN}"
      },
      "description": "Integration with Jira for issue tracking"
    },
    "kubernetes": {
      "command": "python",
      "args": ["-m", "mcp_k8s"],
      "env": {
        "KUBECONFIG": "${KUBECONFIG}"
      },
      "description": "Kubernetes cluster management"
    }
  }
}
```

### Environment Configuration
Set up environment variables for MCP servers:

```bash
# .env (project-specific)
JIRA_URL=https://your-org.atlassian.net
JIRA_TOKEN=your-api-token
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# .env.global (user-specific)
GITHUB_TOKEN=your-github-token
OPENAI_API_KEY=your-openai-key
```

## Technology Stack Customization

### Adding New Stack Guidelines
Create new stack files in `.claude/stacks/`:

```markdown
# .claude/stacks/nextjs.md

# Next.js Development Guidelines

## Project Structure
- `app/` directory for App Router (preferred)
- `components/` for reusable React components
- `lib/` for utility functions and configurations
- `public/` for static assets

## Best Practices
- Use Server Components by default
- Client Components only when needed (`'use client'`)
- Implement proper error boundaries
- Optimize images with next/image
- Use TypeScript with strict mode

## Performance
- Implement proper caching strategies
- Use dynamic imports for code splitting
- Optimize bundle size with tree shaking
- Enable compression and CDN
```

### Technology Detection Updates
Update the detection rules in `CLAUDE.md`:

```markdown
### Detection Rules
- **Next.js files** (`next.config.js`, `app/`, `middleware.ts`) → Refer to @.claude/stacks/nextjs.md
- **Svelte files** (`*.svelte`, `svelte.config.js`) → Refer to @.claude/stacks/svelte.md
- **Flutter files** (`pubspec.yaml`, `lib/*.dart`) → Refer to @.claude/stacks/flutter.md
```

## Automation and Hooks

### Custom Git Hooks
Extend the hooks in `.claude/settings.json`:

```json
{
  "hooks": {
    "beforeBashExecution": {
      "patterns": [
        "git commit*",
        "git push*",
        "npm publish*"
      ],
      "command": "/pre-publish-check"
    },
    "afterEdit": {
      "patterns": ["*.ts", "*.tsx", "*.js", "*.jsx"],
      "command": "/format-code"
    }
  }
}
```

### Custom Automation Commands
Create automation commands:

```markdown
# .claude/commands/pre-publish-check.md

Run comprehensive pre-publish checks:

1. **Export Memory**: Save current session context
2. **Run Tests**: Execute full test suite
3. **Security Scan**: Check for vulnerabilities
4. **Bundle Analysis**: Verify bundle size
5. **Documentation**: Ensure docs are current
6. **Version Check**: Confirm version increment

Fail the operation if any check fails.
```

## Team Collaboration

### Shared Configuration
Create team-wide configuration:

```json
{
  "team": {
    "codeReviewChecklist": [
      "Security vulnerabilities addressed",
      "Tests cover new functionality",
      "Documentation updated",
      "Performance impact considered"
    ],
    "requiredAgents": [
      "researcher", "patterns", "principles", "critic"
    ]
  }
}
```

### Standardized Workflows
Document team workflows in `CLAUDE.md`:

```markdown
## Team Workflows

### Code Reviews
1. Use `/review` command for initial analysis
2. Run security scan with `/security`
3. Check test coverage with `/test`
4. Document findings in PR comments

### Architecture Decisions
1. Use `explorer` agent to generate alternatives
2. Apply `constraints` agent for requirement analysis
3. Get `critic` agent validation before finalizing
4. Export decision to memory system
```

## Environment-Specific Configurations

### Development Environment
```json
{
  "development": {
    "enableDetailedLogging": true,
    "autoFormatOnSave": true,
    "agents": {
      "critic": {
        "strictMode": false
      }
    }
  }
}
```

### Production Environment
```json
{
  "production": {
    "enableDetailedLogging": false,
    "requiredSecurityChecks": true,
    "agents": {
      "critic": {
        "strictMode": true
      }
    }
  }
}
```

## Validation and Testing

### Custom Validation Scripts
Create your own validation scripts:

```bash
#!/bin/bash

# Validate custom configuration
echo "Validating custom configuration..."

# Check custom commands exist
for cmd in deploy monitoring performance; do
    if [ ! -f ".claude/commands/$cmd.md" ]; then
        echo "❌ Missing custom command: $cmd"
        exit 1
    fi
done

# Validate MCP servers
claude mcp status || exit 1

# Check environment variables
required_vars=("JIRA_URL" "DATABASE_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing environment variable: $var"
        exit 1
    fi
done

echo "✅ Custom configuration valid"
```

### Testing Custom Features
Create test scenarios for your customizations:

```bash
# Test custom commands
claude exec "/deploy --dry-run"
claude exec "/performance-check"

# Test agent coordination
claude exec "Use explorer and constraints agents to analyze deployment options"

# Test basic functionality
claude exec "Use explorer and researcher agents to analyze deployment options"
```

## Migration and Updates

### Updating Template Version
When updating the template:

1. **Backup custom configuration**:
   ```bash
   cp -r .claude/ backup-claude-config/
   cp CLAUDE.md backup-claude.md
   ```

2. **Merge new template features**:
   ```bash
   git remote add template https://github.com/ondrasek/ai-code-forge.git
   git fetch template
   git merge template/main
   ```

3. **Restore customizations**:
   - Review conflicts in custom files
   - Update detection rules for new stacks
   - Merge custom agents and commands

4. **Validate configuration**:
   ```bash
   # Test your configuration manually
   claude --version
   claude /help
   ```

### Version Control Best Practices
- Keep custom configuration in version control
- Use branches for experimental customizations
- Document team-specific changes in CLAUDE.md
- Regular backup of memory database (`.mcp/memory.db`)

This customization system allows you to adapt the template to any development workflow while maintaining the powerful agent system, context-clean task coordination, and memory persistence that makes it effective.

---

**Next Steps:**
- 🧠 Configure memory system using scripts/setup-claude-memory.sh
- 📖 See all [Features](features.md) available for customization
- 📚 Return to [Getting Started](getting-started.md)