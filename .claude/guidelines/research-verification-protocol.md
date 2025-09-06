# Research Verification Protocol

<protocol_metadata priority="MEDIUM">
<purpose>Mandatory research process for Zettelkasten notes with dynamic depth</purpose>
<status>REQUIRED - Notes cannot be created without following this protocol</status>
<enforcement>ALL claims MUST be verified or explicitly marked as unverifiable</enforcement>
</protocol_metadata>

<core_principle priority="HIGH">
<definition>Every claim must be verified or explicitly marked as unverifiable</definition>
<foundation>Research is not optional - it is the foundation of note quality</foundation>
<depth_matching>Research depth should match claim complexity</depth_matching>
<enforcement>MANDATORY verification for all claims regardless of perceived obviousness</enforcement>
</core_principle>

<dynamic_research_depth priority="HIGH">
<claim_complexity_assessment priority="HIGH">
  <instruction>Rate each claim 1-5 on all dimensions</instruction>
  
  <dimension name="specificity" priority="MEDIUM">
    <scale_1>Vague claim</scale_1>
    <scale_5>Precise metric</scale_5>
    <enforcement>MUST assess specificity level for research planning</enforcement>
  </dimension>
  
  <dimension name="importance" priority="HIGH">
    <scale_1>Supporting detail</scale_1>
    <scale_5>Core concept</scale_5>
    <enforcement>PRIORITIZE high-importance claims for thorough research</enforcement>
  </dimension>
  
  <dimension name="controversy" priority="HIGH">
    <scale_1>Widely accepted</scale_1>
    <scale_5>Actively debated</scale_5>
    <enforcement>INCREASE research depth for controversial claims</enforcement>
  </dimension>
  
  <dimension name="recency" priority="MEDIUM">
    <scale_1>Established knowledge</scale_1>
    <scale_5>Cutting-edge</scale_5>
    <enforcement>VERIFY currency for recent developments</enforcement>
  </dimension>
</claim_complexity_assessment>

<research_depth_formula priority="HIGH">
  <calculation>Total Score → Required Research</calculation>
  
  <depth_level name="light" priority="MEDIUM" score_range="4-7">
    <requirement>Single authoritative source sufficient</requirement>
    <approach>Official docs or textbooks preferred</approach>
    <verification>One verification search if needed</verification>
    <enforcement>MINIMUM acceptable research for low-complexity claims</enforcement>
  </depth_level>
  
  <depth_level name="medium" priority="HIGH" score_range="8-11">
    <requirement>2-3 diverse sources needed</requirement>
    <approach>Primary source + supporting secondary</approach>
    <verification>Check for recent updates/contradictions</verification>
    <enforcement>STANDARD research depth for most claims</enforcement>
  </depth_level>
  
  <depth_level name="deep" priority="HIGH" score_range="12-16">
    <requirement>4-5 sources including primary research</requirement>
    <approach>Academic search first (Google Scholar)</approach>
    <verification>Cross-reference multiple viewpoints, include historical context</verification>
    <enforcement>COMPREHENSIVE research for complex claims</enforcement>
  </depth_level>
  
  <depth_level name="comprehensive" priority="CRITICAL" score_range="17-20">
    <requirement>Comprehensive literature review (6+ sources)</requirement>
    <approach>Systematic review approach</approach>
    <verification>Include opposing viewpoints, trace citation networks, document evolution of understanding</verification>
    <enforcement>EXHAUSTIVE research for critical claims</enforcement>
  </depth_level>
</research_depth_formula>
</dynamic_research_depth>

<verification_checklist priority="HIGH">
<requirement>Required Before Any Artifact</requirement>

<checklist_format priority="MEDIUM">
  <template>
    Claims Requiring Verification:
    1. [Claim]: _______________
       Research Depth: ___
       Sources Found: ___
       Quality Assessment: ___
       Verification Status: ___
    2. [Next Claim]: _______________
       [Same fields]
  </template>
  <enforcement>MUST document all claims with this format</enforcement>
</checklist_format>

<mandatory_fields priority="HIGH">
  <field name="claim_statement">Exact claim being verified</field>
  <field name="research_depth">Calculated depth level (Light/Medium/Deep/Comprehensive)</field>
  <field name="sources_found">Number and quality of sources located</field>
  <field name="quality_assessment">Source credibility evaluation</field>
  <field name="verification_status">Verified/Unverified/Contradictory Evidence</field>
  <enforcement>ALL fields MUST be completed for each claim</enforcement>
</mandatory_fields>
</verification_checklist>

<search_strategy_framework priority="MEDIUM">
<light_research priority="LOW" depth_range="4-7">
  <approach>Start with official docs or textbooks</approach>
  <verification>One verification search if needed</verification>
  <time_investment>15-30 minutes</time_investment>
  <sources_minimum>1 authoritative source</sources_minimum>
</light_research>

<medium_research priority="MEDIUM" depth_range="8-11">
  <approach>Primary source + supporting secondary</approach>
  <verification>Check for recent updates/contradictions</verification>
  <time_investment>30-60 minutes</time_investment>
  <sources_minimum>2-3 diverse sources</sources_minimum>
</medium_research>

<deep_research priority="HIGH" depth_range="12-16">
  <approach>Academic search first (Google Scholar)</approach>
  <verification>Cross-reference multiple viewpoints</verification>
  <context>Include historical context</context>
  <time_investment>60-120 minutes</time_investment>
  <sources_minimum>4-5 sources including primary research</sources_minimum>
</deep_research>

<comprehensive_research priority="CRITICAL" depth_range="17-20">
  <approach>Systematic review approach</approach>
  <verification>Include opposing viewpoints</verification>
  <analysis>Trace citation networks</analysis>
  <documentation>Document evolution of understanding</documentation>
  <time_investment>2+ hours</time_investment>
  <sources_minimum>6+ sources with literature review methodology</sources_minimum>
</comprehensive_research>
</search_strategy_framework>

<source_prioritization priority="HIGH">
<tier_1_sources priority="CRITICAL">
  <source>Peer-reviewed academic papers</source>
  <source>Official technical documentation</source>
  <source>Government research reports</source>
  <source>Systematic reviews and meta-analyses</source>
  <enforcement>PRIORITIZE these sources for all research</enforcement>
</tier_1_sources>

<tier_2_sources priority="HIGH">
  <source>Academic textbooks from reputable publishers</source>
  <source>Professional organization guidelines</source>
  <source>Expert-authored technical books</source>
  <source>Conference proceedings</source>
  <enforcement>ACCEPTABLE as primary sources when Tier 1 unavailable</enforcement>
</tier_2_sources>

<tier_3_sources priority="MEDIUM">
  <source>Reputable news outlets with fact-checking</source>
  <source>Well-established technical blogs by experts</source>
  <source>High-quality documentation sites</source>
  <source>Community-validated resources</source>
  <enforcement>USE for supporting evidence, not primary claims</enforcement>
</tier_3_sources>

<tier_4_sources priority="LOW">
  <source>Personal blogs</source>
  <source>Social media posts</source>
  <source>Marketing materials</source>
  <source>Unvetted community content</source>
  <enforcement>AVOID as primary sources, use only for leads to better sources</enforcement>
</tier_4_sources>
</source_prioritization>

<research_documentation_requirements priority="HIGH">
<mandatory_documentation priority="HIGH">
  <requirement>Source URL or citation</requirement>
  <requirement>Author credentials assessment</requirement>
  <requirement>Publication date and relevance</requirement>
  <requirement>Key supporting evidence extracted</requirement>
  <requirement>Conflicting information noted</requirement>
  <requirement>Confidence level assigned</requirement>
  <enforcement>DOCUMENT all research findings systematically</enforcement>
</mandatory_documentation>

<confidence_level_scale priority="MEDIUM">
  <level name="high_confidence" score="4-5">Multiple high-quality sources agree, recent verification</level>
  <level name="medium_confidence" score="3">Some sources agree, reasonable verification</level>
  <level name="low_confidence" score="2">Limited sources, some uncertainty</level>
  <level name="uncertain" score="1">Conflicting sources, insufficient evidence</level>
  <level name="unverifiable" score="0">No reliable sources found</level>
  <enforcement>ASSIGN confidence level to every claim</enforcement>
</confidence_level_scale>
</research_documentation_requirements>

<verification_outcomes priority="HIGH">
<verified_claims priority="HIGH">
  <definition>Claims supported by appropriate research depth and source quality</definition>
  <action>Proceed with note creation</action>
  <documentation>Include source references and confidence level</documentation>
</verified_claims>

<partially_verified_claims priority="MEDIUM">
  <definition>Claims with some support but incomplete verification</definition>
  <action>Note limitations explicitly</action>
  <documentation>Specify what remains unverified</documentation>
</partially_verified_claims>

<unverified_claims priority="HIGH">
  <definition>Claims lacking sufficient supporting evidence</definition>
  <action>Mark as unverified or exclude from notes</action>
  <documentation>Document verification attempts</documentation>
  <enforcement>NEVER present unverified claims as facts</enforcement>
</unverified_claims>

<contradictory_evidence priority="CRITICAL">
  <definition>Claims with conflicting evidence from reliable sources</definition>
  <action>Present multiple perspectives with source attribution</action>
  <documentation>Note the controversy and evidence on each side</documentation>
  <enforcement>MANDATORY disclosure of contradictory evidence</enforcement>
</contradictory_evidence>
</verification_outcomes>

<quality_assurance_protocol priority="MEDIUM">
<pre_publication_review priority="MEDIUM">
  <step>Verify all claims have appropriate research depth</step>
  <step>Check source quality meets tier requirements</step>
  <step>Confirm confidence levels are documented</step>
  <step>Review for unverified claims presented as facts</step>
  <step>Validate citation formatting and accessibility</step>
</pre_publication_review>

<periodic_verification_updates priority="LOW">
  <trigger>New contradictory evidence emerges</trigger>
  <trigger>Source reliability changes</trigger>
  <trigger>Field consensus shifts</trigger>
  <action>Update verification status and confidence levels</action>
  <enforcement>MAINTAIN accuracy through periodic review</enforcement>
</periodic_verification_updates>
</quality_assurance_protocol>

<compliance_requirements priority="HIGH">
<mandatory_compliance priority="HIGH">
  <requirement>MUST assess claim complexity using 4-dimension scale</requirement>
  <requirement>MUST apply appropriate research depth formula</requirement>
  <requirement>MUST prioritize higher-tier sources</requirement>
  <requirement>MUST document all research findings</requirement>
  <requirement>MUST assign confidence levels to all claims</requirement>
  <requirement>NEVER present unverified claims as verified facts</requirement>
  <requirement>ALWAYS disclose contradictory evidence</requirement>
</mandatory_compliance>
</compliance_requirements>
EOF < /dev/null