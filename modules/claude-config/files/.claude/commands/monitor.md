---
description: Setup and manage application monitoring, logging, and observability.
argument-hint: Optional monitoring target or service name.
allowed-tools: Task, Read, Write, Edit, Bash
---

# Monitoring and Observability

Setup and manage application monitoring, logging, and observability for performance monitoring, health checks, and alerting configuration.

## Instructions

1. Parse $ARGUMENTS for monitoring parameters:
   - --type [metrics|logs|traces|alerts|health] (monitoring type)
   - --platform [prometheus|grafana|elk|datadog|newrelic|custom] (monitoring platform)
   - --env [dev|staging|prod] (target environment)
   - --services [service-names] (specific services to monitor)
   - --dashboard (generate monitoring dashboards)
   - --alerts (configure alerting rules)
   - --dry-run (preview configuration without applying)

2. Execute parallel clusters for monitoring setup
1. **System Analysis**: context + researcher for application architecture and monitoring requirements
2. **Monitoring Strategy**: performance-optimizer + constraint-solver for performance metrics and resource monitoring
3. **Implementation Planning**: options-analyzer + stack-advisor for monitoring tool selection and configuration
4. **Quality Validation**: principles + critic for monitoring best practices and alerting strategies

PARAMETERS:
--type [metrics|logs|traces|alerts|health] (monitoring type)
--platform [prometheus|grafana|elk|datadog|newrelic|custom] (monitoring platform)
--env [dev|staging|prod] (target environment)
--services [service-names] (specific services to monitor)
--dashboard (generate monitoring dashboards)
--alerts (configure alerting rules)
--dry-run (preview configuration without applying)

OPTIMIZED_PARALLEL_CLUSTERS:
Analysis & Research (2 agents): context + researcher
Performance & Constraints (2 agents): performance-optimizer + constraint-solver
Strategy & Implementation (2 agents): options-analyzer + stack-advisor
Quality & Validation (2 agents): principles + critic

COORDINATION_PROTOCOL: All clusters execute simultaneously via single message with multiple Task() calls for efficient monitoring setup. Total agents: 8 (observability-focused coordination)

INTELLIGENT_OUTPUT:
- **Monitoring Architecture**: Comprehensive observability strategy with tool recommendations
- **Metrics Configuration**: Performance metrics, custom metrics, and KPI tracking
- **Logging Strategy**: Log aggregation, structured logging, and retention policies
- **Alerting Rules**: Intelligent alerting with escalation procedures and noise reduction
- **Dashboard Design**: Monitoring dashboards with visualization and drill-down capabilities
- **Health Checks**: Application and infrastructure health monitoring

## Monitoring Types

### Application Performance Monitoring (APM)
- **Response Times**: API endpoint and page load performance tracking
- **Throughput**: Request volume and processing capacity metrics
- **Error Rates**: Application errors, exceptions, and failure patterns
- **Resource Usage**: CPU, memory, and I/O utilization monitoring

### Infrastructure Monitoring
- **System Metrics**: Server performance, disk usage, and network statistics
- **Container Monitoring**: Docker and Kubernetes resource utilization
- **Database Performance**: Query performance, connection pooling, and deadlocks
- **Network Monitoring**: Latency, bandwidth, and connectivity tracking

### Business Metrics
- **User Analytics**: User behavior, conversion rates, and engagement metrics
- **Feature Usage**: Feature adoption, usage patterns, and performance impact
- **Revenue Metrics**: Transaction volume, revenue tracking, and business KPIs
- **Custom Metrics**: Domain-specific metrics and business logic monitoring

### Security Monitoring
- **Access Patterns**: Authentication attempts, user access, and permission usage
- **Security Events**: Failed logins, suspicious activity, and security violations
- **Compliance Monitoring**: Regulatory compliance and audit trail tracking
- **Vulnerability Scanning**: Security vulnerability detection and remediation

## Platform Integration

### Prometheus & Grafana Stack
- **Metrics Collection**: Prometheus configuration with service discovery
- **Visualization**: Grafana dashboards with custom panels and drill-downs
- **Alerting**: AlertManager configuration with notification channels
- **Service Discovery**: Automatic service detection and metric scraping

### ELK Stack (Elasticsearch, Logstash, Kibana)
- **Log Collection**: Logstash configuration for log parsing and enrichment
- **Storage**: Elasticsearch indexing and retention policies
- **Visualization**: Kibana dashboards and log analysis tools
- **Alerting**: ElastAlert configuration for log-based alerting

### Cloud-Native Solutions
- **AWS CloudWatch**: Metrics, logs, and alarms with AWS service integration
- **Azure Monitor**: Application Insights and Log Analytics integration
- **Google Cloud Monitoring**: Stackdriver monitoring and logging
- **Kubernetes Native**: Prometheus Operator and service mesh monitoring

### Commercial Solutions
- **Datadog**: Full-stack monitoring with APM and infrastructure tracking
- **New Relic**: Application performance monitoring with business insights
- **Splunk**: Enterprise log analysis and security monitoring
- **Dynatrace**: AI-powered application performance monitoring

## Execution Workflow

### Phase 1: System Analysis & Research
```
Task: "Analyze application architecture and monitoring requirements" (context + researcher)
```

### Phase 2: Performance & Strategy Planning
```
Task: "Design performance monitoring and resource constraints" (performance-optimizer + constraint-solver)
Task: "Select monitoring tools and implementation strategy" (options-analyzer + stack-advisor)
```

### Phase 3: Quality Validation & Implementation
```
Task: "Validate monitoring best practices and configuration quality" (principles + critic)
```

**OBSERVABILITY-FOCUSED AGENT COUNT**: 8 agents total (monitoring and observability coordination)

**MEMORY INTEGRATION**: Foundation agents store monitoring patterns and effectiveness for continuous improvement

## Monitoring Output Structure

### Monitoring Strategy
- **Architecture**: Overall monitoring architecture and tool selection
- **Metrics**: Key performance indicators and custom metrics definition
- **Data Flow**: Monitoring data collection, processing, and storage
- **Integration**: Service integration and monitoring coverage

### Configuration Implementation
- **Metrics Collection**: Prometheus, StatsD, or custom metric collection setup
- **Log Aggregation**: Centralized logging configuration and parsing rules
- **Dashboard Configuration**: Grafana, Kibana, or custom dashboard setup
- **Alert Rules**: Alerting thresholds, escalation, and notification setup

### Operational Procedures
- **Runbooks**: Monitoring runbooks and incident response procedures
- **Maintenance**: Monitoring system maintenance and capacity planning
- **Troubleshooting**: Common monitoring issues and resolution procedures
- **Optimization**: Performance tuning and cost optimization strategies

### Security & Compliance
- **Access Control**: Monitoring system access and permission management
- **Data Retention**: Log and metric retention policies for compliance
- **Audit Trails**: Monitoring access and configuration change tracking
- **Privacy**: Data privacy and sensitive information handling

## Health Check Implementation

### Application Health Checks
- **Liveness Probes**: Application availability and basic functionality
- **Readiness Probes**: Service readiness for traffic handling
- **Startup Probes**: Application startup and initialization monitoring
- **Custom Health Checks**: Business logic and dependency health validation

### Infrastructure Health Checks
- **Service Dependency**: External service availability and response times
- **Database Connectivity**: Database connection and query performance
- **Resource Availability**: Disk space, memory, and CPU availability
- **Network Connectivity**: Network connectivity and DNS resolution

### Synthetic Monitoring
- **Endpoint Monitoring**: API endpoint availability and performance
- **User Journey Testing**: Critical user flow monitoring and validation
- **Website Monitoring**: Page load times and functionality testing
- **Mobile App Monitoring**: Mobile application performance and crashes

## Alerting Strategy

### Alert Rule Design
- **Threshold-Based Alerts**: Simple threshold-based alerting for key metrics
- **Anomaly Detection**: Machine learning-based anomaly detection
- **Composite Alerts**: Multi-condition alerts with logical operators
- **Alert Correlation**: Related alert grouping and noise reduction

### Notification Channels
- **Email Notifications**: Email-based alert notifications with formatting
- **Slack Integration**: Real-time team notifications with context
- **PagerDuty Integration**: On-call escalation and incident management
- **Webhook Integration**: Custom notification systems and automation

### Alert Management
- **Alert Fatigue Prevention**: Alert tuning and noise reduction strategies
- **Escalation Procedures**: Alert escalation policies and on-call rotation
- **Alert Acknowledgment**: Alert acknowledgment and resolution tracking
- **Post-Incident Analysis**: Alert effectiveness and tuning recommendations

## Related Commands

- `/deploy` - Deployment monitoring and observability integration
- `/performance` - Performance analysis and optimization coordination
- `/security` - Security monitoring and compliance tracking
- `/test` - Testing strategy integration with monitoring validation

## Best Practices

1. **Observability by Design**: Build monitoring into application architecture
2. **Meaningful Metrics**: Focus on business-relevant metrics and KPIs
3. **Alert Tuning**: Regularly tune alerts to reduce noise and improve signal
4. **Dashboard Design**: Create actionable dashboards with clear visualizations
5. **Incident Response**: Integrate monitoring with incident response procedures
6. **Cost Management**: Monitor monitoring costs and optimize resource usage
7. **Documentation**: Maintain runbooks and monitoring documentation