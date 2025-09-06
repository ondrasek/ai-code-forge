# Critical Thinking Framework for Source Evaluation

<framework_metadata priority="HIGH">
<version>2.0</version>
<purpose>Systematic evaluation of sources and claims with hierarchical quality standards</purpose>
<application>Use during research phase for every source</application>
<enforcement>MUST be applied to ALL sources before accepting claims</enforcement>
</framework_metadata>

<source_quality_hierarchy priority="CRITICAL">
<tier name="gold_standard" priority="CRITICAL" level="1">
  <definition>Highest quality sources requiring minimal additional verification</definition>
  <sources>
    <source>Peer-reviewed journals (Nature, Science, PNAS, domain-specific top journals)</source>
    <source>Systematic reviews and meta-analyses</source>
    <source>Official technical documentation (RFCs, language specs, API docs)</source>
    <source>Primary research with reproducible methodology</source>
  </sources>
  <enforcement>PRIORITIZE these sources over all others when available</enforcement>
</tier>

<tier name="high_quality_secondary" priority="HIGH" level="2">
  <definition>High-quality sources with established peer review processes</definition>
  <sources>
    <source>Academic textbooks from reputable publishers</source>
    <source>Technical books with strong peer review (O'Reilly, Manning, etc.)</source>
    <source>Official organizational reports (WHO, IEEE, ACM)</source>
    <source>Established technical blogs with author expertise (e.g., Martin Fowler for software)</source>
  </sources>
  <enforcement>ACCEPTABLE for primary claims when Tier 1 unavailable</enforcement>
</tier>

<tier name="acceptable_supporting" priority="MEDIUM" level="3">
  <definition>Acceptable sources requiring additional verification for critical claims</definition>
  <sources>
    <source>Reputable news outlets with fact-checking (Reuters, AP, BBC)</source>
    <source>Community-validated resources (high-quality Stack Overflow answers with votes)</source>
    <source>Conference proceedings and white papers</source>
    <source>Well-maintained documentation (MDN, official tutorials)</source>
  </sources>
  <enforcement>USE for supporting evidence, require verification for primary claims</enforcement>
</tier>

<tier name="extreme_caution" priority="HIGH" level="4">
  <definition>Sources requiring extensive verification and explicit limitation notation</definition>
  <sources>
    <source>Personal blogs without clear expertise</source>
    <source>Medium/Substack unless author is recognized expert</source>
    <source>YouTube/Video content unless from educational institutions</source>
    <source>Any source trying to sell something</source>
  </sources>
  <enforcement>NEVER use as sole source, ALWAYS note limitations explicitly</enforcement>
</tier>

<decision_rule priority="CRITICAL">
  <rule>Always prefer highest tier available. If only Tier 3-4 available, explicitly note limitation</rule>
  <enforcement>MANDATORY tier assessment for every source</enforcement>
</decision_rule>
</source_quality_hierarchy>

<source_credibility_assessment priority="CRITICAL">
<primary_questions priority="CRITICAL">
  <instruction>Ask for EVERY source without exception</instruction>
  
  <question_category name="authority" priority="CRITICAL">
    <question>Who is the author/organization?</question>
    <question>What are their credentials in this field?</question>
    <question>Is this their area of expertise?</question>
    <question>Are they cited by others in the field?</question>
    <enforcement>MUST establish author credibility before accepting claims</enforcement>
  </question_category>

  <question_category name="source_type_hierarchy" priority="HIGH">
    <hierarchy>
      <level priority="CRITICAL">Primary source (original research/direct evidence)</level>
      <level priority="HIGH">Secondary source (analysis/interpretation)</level>
      <level priority="MEDIUM">Tertiary source (encyclopedia/aggregator)</level>
      <level priority="LOW">Opinion/Editorial (clearly marked viewpoint)</level>
    </hierarchy>
    <enforcement>ALWAYS identify source type and prioritize accordingly</enforcement>
  </question_category>

  <question_category name="publication_quality" priority="HIGH">
    <quality_levels>
      <level priority="CRITICAL">Peer-reviewed journal article</level>
      <level priority="HIGH">Academic institution publication</level>
      <level priority="HIGH">Professional organization report</level>
      <level priority="MEDIUM">Reputable news outlet with fact-checking</level>
      <level priority="LOW">Blog/Personal website (evaluate carefully)</level>
    </quality_levels>
    <enforcement>MUST assess publication quality before accepting claims</enforcement>
  </question_category>

  <question_category name="recency_relevance" priority="MEDIUM">
    <question>When published/last updated?</question>
    <question>Is this current for the topic?</question>
    <question>Have there been major developments since?</question>
    <question>Does date matter for this claim?</question>
    <enforcement>VERIFY currency for time-sensitive topics</enforcement>
  </question_category>

  <question_category name="transparency" priority="HIGH">
    <question>Are sources and methods clear?</question>
    <question>Is raw data available?</question>
    <question>Are limitations acknowledged?</question>
    <question>Is uncertainty quantified?</question>
    <enforcement>REQUIRE transparency for scientific/technical claims</enforcement>
  </question_category>
</primary_questions>

<red_flags priority="CRITICAL">
<immediate_concerns priority="HIGH">
  <flag>No author or organization listed</flag>
  <flag>No date or "timeless" content</flag>
  <flag>No sources cited for factual claims</flag>
  <flag>Obvious spelling/grammar errors</flag>
  <flag>Sensationalist headlines</flag>
  <flag>Domain looks suspicious</flag>
  <flag>Vendor marketing content (especially product/service claims)</flag>
  <enforcement>INVESTIGATE further when any flags present</enforcement>
</immediate_concerns>

<disqualifying_factors priority="CRITICAL">
  <factor>Known disinformation source</factor>
  <factor>Extreme bias without disclosure</factor>
  <factor>Pure marketing material disguised as research</factor>
  <factor>Selling something related to claims</factor>
  <factor>Conspiracy theory promotion</factor>
  <factor>Hate speech or extremism</factor>
  <enforcement>IMMEDIATELY REJECT sources with these factors</enforcement>
</disqualifying_factors>
</red_flags>
</source_credibility_assessment>

<claim_evaluation_process priority="HIGH">
<evidence_quality_assessment priority="HIGH">
  <strong_evidence priority="HIGH">
    <criteria>Multiple independent sources agree</criteria>
    <criteria>Primary research with methodology</criteria>
    <criteria>Statistical significance shown</criteria>
    <criteria>Reproducible results</criteria>
    <enforcement>ACCEPT claims with strong evidence</enforcement>
  </strong_evidence>

  <weak_evidence priority="MEDIUM">
    <criteria>Single source only</criteria>
    <criteria>Anecdotal evidence</criteria>
    <criteria>No methodology provided</criteria>
    <criteria>Cherry-picked data</criteria>
    <enforcement>REQUIRE additional verification for weak evidence</enforcement>
  </weak_evidence>

  <insufficient_evidence priority="HIGH">
    <criteria>No supporting data</criteria>
    <criteria>Opinion presented as fact</criteria>
    <criteria>Correlation claimed as causation</criteria>
    <criteria>Extraordinary claims without extraordinary evidence</criteria>
    <enforcement>REJECT claims with insufficient evidence</enforcement>
  </insufficient_evidence>
</evidence_quality_assessment>

<logical_fallacy_detection priority="MEDIUM">
  <fallacy>Appeal to authority (without relevant expertise)</fallacy>
  <fallacy>False dichotomy (only two options presented)</fallacy>
  <fallacy>Straw man arguments (misrepresenting opposition)</fallacy>
  <fallacy>Ad hominem attacks (attacking person, not argument)</fallacy>
  <fallacy>Confirmation bias (cherry-picking supporting evidence)</fallacy>
  <enforcement>IDENTIFY and NOTE fallacies when present</enforcement>
</logical_fallacy_detection>
</claim_evaluation_process>

<quick_evaluation_checklist priority="HIGH">
<instruction>For every source, quickly check all items</instruction>
<checklist priority="HIGH">
  <check>Author/organization identified?</check>
  <check>Expertise in this topic?</check>
  <check>Date recent enough?</check>
  <check>Sources cited?</check>
  <check>Bias disclosed?</check>
  <check>Methods explained?</check>
  <check>Limitations acknowledged?</check>
  <check>Other sources agree?</check>
  <check>Evidence matches claims?</check>
  <check>Free from marketing intent?</check>
  <check>Free from major red flags?</check>
  <check>What quality tier (1-4)?</check>
</checklist>

<scoring_guidelines priority="MEDIUM">
  <score range="10-12">Likely credible (Tier 1-2)</score>
  <score range="6-9">Evaluate carefully (Tier 2-3)</score>
  <score range="0-5">Probably not credible (Tier 4)</score>
  <enforcement>APPLY scoring consistently to all sources</enforcement>
</scoring_guidelines>
</quick_evaluation_checklist>

<marketing_content_protocol priority="HIGH">
<identification priority="HIGH">
  <obvious_marketing>Product pages, sales brochures, vendor websites</obvious_marketing>
  <disguised_marketing>White papers, "research reports," case studies</disguised_marketing>
  <subtle_marketing>Sponsored content, native advertising, paid placements</subtle_marketing>
  <academic_looking_marketing>Vendor-funded studies without disclosure</academic_looking_marketing>
  <enforcement>ALWAYS identify marketing intent before evaluation</enforcement>
</identification>

<handling_protocol priority="CRITICAL">
  <rule>NEVER use as primary source for comparative claims</rule>
  <rule>CAN use for: Technical specifications, feature lists</rule>
  <rule>ALWAYS verify: Any performance claims independently</rule>
  <rule>LOOK for: Independent reviews, third-party testing</rule>
  <enforcement>MANDATORY protocol for all marketing content</enforcement>
</handling_protocol>

<red_flag_phrases priority="MEDIUM">
  <phrase>"Industry-leading"</phrase>
  <phrase>"Revolutionary breakthrough"</phrase>
  <phrase>"The only solution that..."</phrase>
  <phrase>"Studies show" (without citation)</phrase>
  <phrase>"Customers report" (without data)</phrase>
  <enforcement>FLAG sources using these phrases for additional scrutiny</enforcement>
</red_flag_phrases>

<marketing_encounter_procedure priority="HIGH">
  <step>Mark source as vendor/marketing</step>
  <step>Extract only factual specifications</step>
  <step>Seek independent verification</step>
  <step>Note potential bias in research transparency</step>
  <step>NEVER present marketing claims as verified facts</step>
</marketing_encounter_procedure>
</marketing_content_protocol>

<operational_guidelines priority="HIGH">
<final_reminders priority="MEDIUM">
  <reminder>No source is perfect - Even good sources have limitations</reminder>
  <reminder>Triangulate - Never rely on single source for important claims</reminder>
  <reminder>Document doubts - If unsure, say so in the note</reminder>
  <reminder>Update regularly - Knowledge evolves, so should notes</reminder>
  <reminder>Prefer primary - Get as close to original source as possible</reminder>
  <reminder>Check yourself - Are your own biases affecting evaluation?</reminder>
  <reminder>Quality over quantity - One Tier 1 source beats five Tier 4 sources</reminder>
</final_reminders>

<uncertainty_protocol priority="HIGH">
  <condition>If you cannot determine credibility</condition>
  <action>Mark as "uncertain pending verification"</action>
  <action>Document what would be needed to verify</action>
  <action>Search for additional sources</action>
  <action>Consider reaching out to experts</action>
  <action>Default to transparency about limitations</action>
  <principle>It's better to admit uncertainty than to present dubious claims as facts</principle>
  <enforcement>ALWAYS prioritize transparency over false confidence</enforcement>
</uncertainty_protocol>
</operational_guidelines>

<mandatory_compliance priority="CRITICAL">
<core_requirements priority="CRITICAL">
  <requirement>MUST assess every source using tier hierarchy</requirement>
  <requirement>MUST apply credibility assessment questions to all sources</requirement>
  <requirement>MUST identify and flag marketing content</requirement>
  <requirement>MUST document limitations and uncertainties</requirement>
  <requirement>MUST prioritize higher-tier sources</requirement>
  <requirement>NEVER accept claims without evidence evaluation</requirement>
</core_requirements>
</mandatory_compliance>
EOF < /dev/null