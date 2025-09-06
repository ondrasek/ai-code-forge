# Multi-Agent Security Workflow Combinations

<overview priority="CRITICAL">
<definition>Powerful multi-agent workflow combinations enabled by specialized security agents with extended thinking pattern integration for comprehensive security analysis</definition>
<enforcement>ALL security workflows MUST follow designated agent sequences to ensure complete coverage</enforcement>
</overview>

<core_security_agents priority="CRITICAL">
<agent_definitions>
  <vulnerability_scanner priority="CRITICAL">
    <pattern>Security pattern matching/scanning</pattern>
    <focus>Code-level security flaw detection using OWASP/CVE</focus>
    <integrations>researcher (CVE lookup) + patterns (anti-patterns) + critic (risk validation)</integrations>
    <enforcement>MUST be used for all code-level security assessments</enforcement>
  </vulnerability_scanner>

  <threat_modeling priority="CRITICAL">
    <pattern>Attack surface analysis/systems thinking</pattern>
    <focus>Architectural security risk assessment</focus>
    <integrations>context (architecture) + researcher (threat intel) + constraints (trade-offs) + critic (validation)</integrations>
    <enforcement>REQUIRED for all architectural security reviews</enforcement>
  </threat_modeling>

  <compliance_checker priority="HIGH">
    <pattern>Rule-based compliance assessment</pattern>
    <focus>Regulatory standard evaluation (SOC2, GDPR, HIPAA)</focus>
    <integrations>researcher (regulations) + patterns (compliance anti-patterns) + context (scope) + constraints (feasibility) + critic (audit risk)</integrations>
    <enforcement>MANDATORY for all systems handling regulated data</enforcement>
  </compliance_checker>
</agent_definitions>
</core_security_agents>

<comprehensive_security_workflows priority="CRITICAL">
<workflow name="complete_security_assessment" priority="CRITICAL">
  <definition>Full security review of system or codebase with comprehensive coverage</definition>
  <use_case>Complete security review of system or codebase</use_case>
  <sequence>
    <step order="1">vulnerability-scanner: Initial OWASP Top 10 scan</step>
    <step order="2">researcher: "Research CVE database for detected frameworks and versions"</step>
    <step order="3">patterns: "Find structural security anti-patterns in authentication/authorization logic"</step>
    <step order="4">threat-modeling: "Model attack surface and threat scenarios for system architecture"</step>
    <step order="5">context: "Map system architecture showing security-relevant data flows"</step>
    <step order="6">compliance-checker: "Assess regulatory compliance for detected data types and industry"</step>
    <step order="7">researcher: "Research compliance requirements and recent enforcement actions"</step>
    <step order="8">critic: "Evaluate if identified security issues represent real vs theoretical risks"</step>
    <step order="9">constraints: "Balance security recommendations with operational feasibility"</step>
    <step order="10">SYNTHESIZE: Comprehensive security assessment with prioritized recommendations</step>
  </sequence>
  <validation>✅ All 10 steps completed, ✅ Prioritized recommendations produced, ✅ Risk assessment validated</validation>
</workflow>

<workflow name="web_application_security_review" priority="HIGH">
  <definition>Security analysis specifically optimized for web applications</definition>
  <use_case>Security analysis for web applications</use_case>
  <sequence>
    <step order="1">vulnerability-scanner: Scan for web app vulnerabilities (OWASP Top 10)</step>
    <step order="2">researcher: "Research recent web application attack trends and CVEs"</step>
    <step order="3">threat-modeling: "Model web application attack surface and user access patterns"</step>
    <step order="4">patterns: "Detect insecure coding patterns in authentication and session management"</step>
    <step order="5">compliance-checker: "Check web application privacy and data protection compliance"</step>
    <step order="6">critic: "Assess realistic exploitability of web application vulnerabilities"</step>
    <step order="7">RESULT: Web-specific security assessment with attack scenarios</step>
  </sequence>
  <validation>✅ OWASP Top 10 coverage, ✅ Attack scenarios documented, ✅ Exploitability assessed</validation>
</workflow>

<workflow name="enterprise_compliance_audit" priority="HIGH">
  <definition>Regulatory compliance preparation with audit-ready documentation</definition>
  <use_case>Regulatory compliance preparation</use_case>
  <sequence>
    <step order="1">compliance-checker: Initial compliance framework assessment</step>
    <step order="2">researcher: "Research latest regulatory requirements and enforcement guidance"</step>
    <step order="3">context: "Map compliance scope to system architecture and data handling"</step>
    <step order="4">patterns: "Find compliance anti-patterns in data handling and access controls"</step>
    <step order="5">vulnerability-scanner: "Scan for security vulnerabilities affecting compliance"</step>
    <step order="6">threat-modeling: "Model regulatory compliance threat scenarios"</step>
    <step order="7">constraints: "Assess compliance implementation vs operational requirements"</step>
    <step order="8">critic: "Evaluate audit risk and remediation priorities"</step>
    <step order="9">RESULT: Audit-ready compliance assessment with evidence gaps identified</step>
  </sequence>
  <validation>✅ Audit-ready status, ✅ Evidence gaps identified, ✅ Remediation priorities set</validation>
</workflow>

<workflow name="incident_response_security_analysis" priority="CRITICAL">
  <definition>Post-incident security analysis with comprehensive threat assessment</definition>
  <use_case>Post-incident security analysis</use_case>
  <sequence>
    <step order="1">vulnerability-scanner: Scan for vulnerabilities related to incident</step>
    <step order="2">threat-modeling: "Model attack path and lateral movement possibilities"</step>
    <step order="3">patterns: "Find similar vulnerable patterns across system"</step>
    <step order="4">researcher: "Research attack techniques and indicators of compromise"</step>
    <step order="5">compliance-checker: "Assess compliance implications and breach notification requirements"</step>
    <step order="6">critic: "Evaluate containment effectiveness and residual risks"</step>
    <step order="7">RESULT: Comprehensive incident analysis with remediation plan</step>
  </sequence>
  <validation>✅ Attack path mapped, ✅ Containment validated, ✅ Remediation plan ready</validation>
</workflow>
</comprehensive_security_workflows>

<specialized_security_combinations priority="MEDIUM">
<combination name="api_security_assessment" priority="HIGH">
  <sequence>vulnerability-scanner → patterns → threat-modeling → critic</sequence>
  <focus>API endpoint security, authentication flaws, data exposure</focus>
  <validation>✅ Endpoint security validated, ✅ Authentication tested, ✅ Data exposure assessed</validation>
</combination>

<combination name="data_privacy_analysis" priority="HIGH">
  <sequence>compliance-checker → patterns → researcher → constraints → critic</sequence>
  <focus>GDPR/CCPA compliance, data handling practices, privacy controls</focus>
  <validation>✅ Privacy regulations compliance, ✅ Data handling validated, ✅ Privacy controls verified</validation>
</combination>

<combination name="architecture_security_review" priority="MEDIUM">
  <sequence>threat-modeling → context → vulnerability-scanner → constraints → critic</sequence>
  <focus>System design security, trust boundaries, attack surface reduction</focus>
  <validation>✅ Trust boundaries defined, ✅ Attack surface minimized, ✅ Design security validated</validation>
</combination>

<combination name="database_security_assessment" priority="MEDIUM">
  <sequence>vulnerability-scanner → patterns → threat-modeling → compliance-checker</sequence>
  <focus>SQL injection, data encryption, access controls, audit trails</focus>
  <validation>✅ SQL injection prevented, ✅ Encryption verified, ✅ Access controls validated, ✅ Audit trails confirmed</validation>
</combination>
</specialized_security_combinations>

<operational_enforcement priority="CRITICAL">
<mandatory_practices>
  <practice>NEVER skip security workflow steps - each contributes essential coverage</practice>
  <practice>ALWAYS validate outputs using designated validation criteria</practice>
  <practice>MUST prioritize CRITICAL workflows for all security assessments</practice>
  <practice>REQUIRE agent coordination following specified sequences</practice>
</mandatory_practices>
</operational_enforcement>
EOF < /dev/null