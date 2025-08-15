---
description: Automate deployment processes and infrastructure management with safety checks.
argument-hint: Optional deployment target environment.
allowed-tools: Task, Bash, Read, Write, Glob
---

# Deployment Automation

!`git status`
!`git tag --list | tail -5`

Automate deployment processes and infrastructure management with multi-environment deployment, safety checks and rollback capabilities.

## Instructions

1. Parse $ARGUMENTS for deployment parameters:
   - --env [dev|staging|prod] (target environment)
   - --strategy [rolling|blue-green|canary] (deployment strategy)
   - --dry-run (preview deployment without execution)
   - --rollback (rollback to previous version)
   - --health-check (include health validation)
   - --docker (containerized deployment)
   - FILES... (specific deployment configurations)

2. Execute parallel agent clusters for deployment planning
1. **Deployment Context Analysis**: context agent for environment and infrastructure understanding
2. **Infrastructure Planning**: constraint-solver + options-analyzer for deployment strategy and resource constraints
3. **Safety Validation**: critic + principles for deployment safety and best practices
4. **Implementation Coordination**: code-cleaner + stack-advisor for deployment scripts and technology-specific guidance

PARAMETERS:
--env [dev|staging|prod] (target environment)
--strategy [rolling|blue-green|canary] (deployment strategy)
--dry-run (preview deployment without execution)
--rollback (rollback to previous version)
--health-check (include health validation)
--docker (containerized deployment)
FILES... (specific deployment configurations)

OPTIMIZED_PARALLEL_CLUSTERS:
Context & Planning (3 agents): context + constraint-solver + options-analyzer
Safety & Standards (2 agents): critic + principles  
Implementation (2 agents): code-cleaner + stack-advisor

COORDINATION_PROTOCOL: All clusters execute simultaneously via single message with multiple Task() calls for efficient deployment planning. Total agents: 7 (deployment-focused coordination)

INTELLIGENT_OUTPUT:
- **Environment Analysis**: Target environment assessment and readiness validation
- **Deployment Strategy**: Recommended approach with risk assessment and resource requirements
- **Infrastructure Setup**: Container, networking, and service configuration
- **Safety Checks**: Pre-deployment validation and rollback procedures
- **Implementation Plan**: Step-by-step deployment execution with monitoring
- **Post-Deployment**: Health checks and success validation

## Deployment Strategies

### Rolling Deployment
- **Use Case**: Standard production deployments with minimal downtime
- **Process**: Gradual replacement of instances with health checks
- **Safety**: Automatic rollback on health check failures
- **Monitoring**: Real-time deployment progress tracking

### Blue-Green Deployment
- **Use Case**: Zero-downtime deployments with instant rollback capability
- **Process**: Full environment duplication with traffic switching
- **Safety**: Complete environment validation before traffic switch
- **Monitoring**: Side-by-side environment comparison

### Canary Deployment
- **Use Case**: High-risk deployments requiring gradual rollout
- **Process**: Percentage-based traffic routing to new version
- **Safety**: Metrics-based automatic promotion or rollback
- **Monitoring**: Detailed performance and error rate tracking

## Infrastructure Support

### Container Orchestration
- **Docker**: Container image building and registry management
- **Kubernetes**: Pod deployment and service configuration
- **Docker Compose**: Multi-service local deployments
- **Registry**: Image versioning and security scanning

### Cloud Platforms
- **AWS**: ECS, EKS, Lambda deployment patterns
- **Azure**: AKS, Container Instances, Functions
- **GCP**: GKE, Cloud Run, Cloud Functions
- **Platform-agnostic**: Generic cloud deployment patterns

### Infrastructure as Code
- **Terraform**: Infrastructure provisioning and management
- **CloudFormation**: AWS-specific infrastructure templates
- **Pulumi**: Modern infrastructure as code with multiple languages
- **Ansible**: Configuration management and application deployment

## Execution Workflow

### Phase 1: Environment Analysis & Planning
```
Task: "Analyze deployment context and target environment" (context)
Task: "Plan deployment strategy with constraint analysis" (constraint-solver + options-analyzer)
```

### Phase 2: Safety & Implementation Validation
```
Task: "Validate deployment safety and best practices" (critic + principles + code-cleaner + stack-advisor)
```

**DEPLOYMENT-FOCUSED AGENT COUNT**: 7 agents total (environment and infrastructure coordination)

**MEMORY INTEGRATION**: Foundation agents store deployment patterns and outcomes for continuous improvement

## Deployment Output Structure

### Deployment Summary
- **Environment**: Target deployment environment and configuration
- **Strategy**: Selected deployment approach with justification
- **Infrastructure**: Required resources and service configuration
- **Timeline**: Estimated deployment duration and steps

### Pre-Deployment Validation
- **Environment Readiness**: Infrastructure and service dependencies
- **Configuration Validation**: Environment variables and secrets
- **Resource Availability**: Compute, storage, and network capacity
- **Security Compliance**: Access controls and security policies

### Deployment Execution
- **Infrastructure Setup**: Container, networking, and load balancer configuration
- **Application Deployment**: Service deployment with health monitoring
- **Traffic Management**: Load balancing and routing configuration
- **Monitoring Integration**: Logging, metrics, and alerting setup

### Post-Deployment Verification
- **Health Checks**: Application and service health validation
- **Performance Metrics**: Response times and resource utilization
- **Rollback Procedures**: Automated rollback triggers and manual procedures
- **Success Criteria**: Deployment completion validation

## Safety Protocols

### Pre-Deployment Checks
- Configuration validation and environment readiness
- Resource availability and capacity planning
- Security policy compliance and access control validation
- Backup and rollback procedure verification

### During Deployment
- Real-time health monitoring and error detection
- Automatic rollback triggers for critical failures
- Progressive deployment with validation gates
- Service dependency management and coordination

### Post-Deployment
- Comprehensive health validation and performance monitoring
- Log aggregation and error tracking setup
- Alerting configuration and escalation procedures
- Documentation updates and deployment logging

## Related Commands

- `/monitor` - Setup monitoring and observability for deployed applications
- `/test` - Pre-deployment testing and validation strategies
- `/security` - Security analysis and compliance validation for deployments
- `/stacks` - Technology-specific deployment guidance and best practices

## Best Practices

1. **Infrastructure as Code**: Version control all infrastructure configurations
2. **Automated Testing**: Comprehensive testing before production deployment
3. **Progressive Deployment**: Use canary or blue-green for high-risk changes
4. **Monitoring Integration**: Setup observability before deployment completion
5. **Rollback Readiness**: Always have tested rollback procedures
6. **Security First**: Validate security policies and access controls
7. **Documentation**: Maintain deployment runbooks and incident procedures