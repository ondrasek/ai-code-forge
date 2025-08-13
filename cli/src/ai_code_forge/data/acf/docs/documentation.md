# Documentation Maintenance Instructions

## Automatic Documentation Updates
- **Always update documentation** when making code changes
- **Same commit rule**: Documentation updates go in the same commit as code changes
- **Files to maintain**: README.md, CHANGELOG.md, API documentation, CLAUDE.md
- **What to update**:
  - New features: Add to README features section
  - API changes: Update API documentation
  - Configuration changes: Update setup instructions
  - Breaking changes: Add to CHANGELOG with migration guide
  - New dependencies: Update installation instructions

## Documentation Checklist
Before committing, check if your changes affect:
- [ ] README.md - Features, installation, usage
- [ ] CHANGELOG.md - Version history, breaking changes
- [ ] API docs - Endpoint changes, new methods
- [ ] Configuration docs - New settings, environment variables
- [ ] CLAUDE.md - Development guidelines, patterns

## Using the Documentation Agent
Use the `docsync` agent to help maintain documentation:
```
Task: Use the docsync agent to update documentation after adding the new caching feature
```

## Documentation Standards
- Use clear, concise language
- Include code examples where helpful
- Keep formatting consistent with existing docs
- Test all code examples before committing
- Update table of contents when adding sections