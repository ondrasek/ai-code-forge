---
description: Generate code components, services, and project scaffolding with templates.
argument-hint: Component or service NAME to generate.
allowed-tools: Task, Write, Read, MultiEdit, Bash
---

# Code Generation

Generate code components, services, and project scaffolding with framework-agnostic code generation and customizable templates.

## Instructions

1. Parse $ARGUMENTS for generation parameters:
   - --type [component|service|api|model|test|config] (generation type)
   - --framework [react|vue|angular|express|fastapi|django|spring] (target framework)
   - --template [custom-template-path] (use custom template)
   - --output [output-directory] (generation target directory)
   - --dry-run (preview generation without creating files)
   - --overwrite (overwrite existing files)
   - NAME (component/service name)

2. Execute optimized parallel clusters for code generation
1. **Template Analysis**: patterns + researcher for code pattern recognition and template validation
2. **Generation Strategy**: options-analyzer + stack-advisor for framework-specific generation approaches
3. **Quality Validation**: principles + critic for generated code quality and best practices
4. **Implementation**: code-cleaner + meta-programmer for code generation and template processing

PARAMETERS:
--type [component|service|api|model|test|config] (generation type)
--framework [react|vue|angular|express|fastapi|django|spring] (target framework)
--template [custom-template-path] (use custom template)
--output [output-directory] (generation target directory)  
--dry-run (preview generation without creating files)
--overwrite (overwrite existing files)
NAME (component/service name)

OPTIMIZED_PARALLEL_CLUSTERS:
Pattern & Research (2 agents): patterns + researcher
Strategy & Framework (2 agents): options-analyzer + stack-advisor
Quality & Implementation (4 agents): principles + critic + code-cleaner + meta-programmer

COORDINATION_PROTOCOL: All clusters execute simultaneously via single message with multiple Task() calls for efficient code generation. Total agents: 8 (generation-focused coordination)

INTELLIGENT_OUTPUT:
- **Template Analysis**: Available templates and pattern matching for target framework
- **Generation Plan**: Files to be created with structure and dependencies
- **Code Quality**: Generated code adherence to best practices and conventions  
- **Framework Integration**: Technology-specific optimizations and configurations
- **Testing Strategy**: Generated test files and validation approaches
- **Documentation**: Generated documentation and usage examples

## Generation Types

### Component Generation
- **Frontend Components**: React, Vue, Angular components with props/state
- **Backend Components**: Service classes, utilities, and helpers
- **Templates**: Component structure, styling, and test files
- **Integration**: Import statements and dependency injection

### Service Generation  
- **API Services**: RESTful service classes with CRUD operations
- **Business Logic**: Service layer implementations with validation
- **Database Services**: Repository patterns and data access layers
- **External Integrations**: Third-party service wrappers and clients

### API Generation
- **Endpoint Generation**: Route handlers with request/response types
- **OpenAPI Specifications**: Swagger/OpenAPI documentation generation
- **Validation Schemas**: Request/response validation with error handling
- **Authentication**: JWT, OAuth, and session-based auth patterns

### Model Generation
- **Database Models**: ORM models with relationships and constraints
- **Data Transfer Objects**: Request/response DTOs with validation
- **Type Definitions**: TypeScript interfaces and type guards
- **Schema Migrations**: Database migration files for model changes

### Test Generation
- **Unit Tests**: Component and service test files with mocks
- **Integration Tests**: API and database integration test suites
- **E2E Tests**: End-to-end test scenarios and page objects
- **Test Utilities**: Mock factories and test data generators

### Configuration Generation
- **Environment Configs**: Environment-specific configuration files
- **Build Configurations**: Webpack, Vite, and build tool configs
- **CI/CD Pipelines**: GitHub Actions, GitLab CI, and Jenkins files
- **Docker Configurations**: Dockerfiles and docker-compose files

## Framework Support

### Frontend Frameworks
- **React**: Components, hooks, context providers, and routing
- **Vue**: Components, composables, stores, and router configuration
- **Angular**: Components, services, modules, and routing
- **Svelte**: Components, stores, and routing with SvelteKit

### Backend Frameworks
- **Node.js**: Express, Fastify, NestJS service and controller generation
- **Python**: Django, FastAPI, Flask models and view generation
- **Java**: Spring Boot controllers, services, and entity generation
- **C#**: ASP.NET Core controllers, services, and model generation

### Full-Stack Templates
- **Next.js**: Full-stack React applications with API routes
- **Nuxt.js**: Full-stack Vue applications with server-side rendering
- **T3 Stack**: TypeScript, Next.js, Prisma, and tRPC
- **MEAN/MERN**: MongoDB, Express, Angular/React, Node.js stacks

## Execution Workflow

### Phase 1: Template Analysis & Framework Detection
```
Task: "Analyze code patterns and validate templates" (patterns + researcher)
Task: "Determine generation strategy and framework specifics" (options-analyzer + stack-advisor)
```

### Phase 2: Quality Validation & Code Generation
```
Task: "Validate quality standards and generate code" (principles + critic + code-cleaner + meta-programmer)
```

**GENERATION-FOCUSED AGENT COUNT**: 8 agents total (template and code generation coordination)

**MEMORY INTEGRATION**: Foundation agents store generation patterns and template effectiveness for continuous improvement

## Generation Output Structure

### Generation Summary
- **Type**: Generation type and target framework
- **Templates**: Selected templates and customization options
- **Files**: List of files to be generated with descriptions
- **Dependencies**: Required packages and configuration changes

### Generated Code Structure
- **File Organization**: Directory structure and file naming conventions
- **Code Patterns**: Applied design patterns and architectural decisions
- **Dependencies**: Import statements and package requirements
- **Configuration**: Framework-specific configuration and setup

### Quality Validation
- **Code Standards**: Adherence to language and framework conventions
- **Best Practices**: Implementation of recommended patterns and practices
- **Security**: Security considerations and vulnerability prevention
- **Performance**: Optimization opportunities and performance considerations

### Integration Guide
- **Setup Instructions**: Steps to integrate generated code into existing project
- **Configuration Changes**: Required configuration file modifications
- **Testing**: How to test generated components and services
- **Documentation**: Usage examples and API documentation

## Template System

### Built-in Templates
- **Component Templates**: Standard component structures for each framework
- **Service Templates**: Business logic and data access layer templates
- **API Templates**: RESTful API endpoints with standard patterns
- **Test Templates**: Comprehensive test coverage templates

### Custom Templates
- **Template Creation**: Guidelines for creating custom generation templates
- **Variable Substitution**: Template variable system and customization options
- **Template Validation**: Quality checks and template testing procedures
- **Template Sharing**: Repository and sharing mechanisms for templates

### Template Validation
- **Syntax Checking**: Template syntax validation and error detection
- **Output Validation**: Generated code quality and standards compliance
- **Framework Compatibility**: Template compatibility with target frameworks
- **Security Scanning**: Template security analysis and vulnerability detection

## Integration Patterns

### Existing Project Integration
- **Code Analysis**: Existing codebase analysis for integration patterns
- **Dependency Management**: Package and dependency conflict resolution
- **Configuration Merging**: Integration with existing configuration files
- **Import Organization**: Automatic import statement generation and organization

### Build System Integration
- **Webpack Integration**: Automatic webpack configuration updates
- **Vite Integration**: Vite plugin and configuration management
- **Build Script Updates**: Package.json script updates and optimization
- **Asset Management**: Static asset handling and optimization

## Related Commands

- `/stacks` - Technology stack analysis and framework-specific guidance
- `/test` - Generated code testing strategies and validation
- `/refactor` - Code improvement and pattern optimization for generated code
- `/doc-update` - Documentation updates for generated components and services

## Best Practices

1. **Template Validation**: Always validate templates before generation
2. **Code Review**: Review generated code for quality and security
3. **Testing Integration**: Generate comprehensive test coverage
4. **Documentation**: Include usage documentation with generated code
5. **Version Control**: Commit templates and generated code separately
6. **Customization**: Prefer configuration over code modification
7. **Security**: Validate generated code for security vulnerabilities