# Decision Rationale: GitHub Issue Duplicate Detection System Implementation

## EXECUTIVE SUMMARY

**Recommended Approach**: Agent-delegated command using GitHub CLI with lightweight similarity analysis, conservative confidence thresholds, and semi-automated workflow with human oversight.

**Key Decision**: Prioritize **reliability and user trust** over **sophisticated detection algorithms** based on analysis of security implications, maintainability, and integration with existing codebase patterns.

## IMPLEMENTATION APPROACH ANALYSIS

### 1. COMMAND STRUCTURE DECISION

**CHOSEN**: Modular Agent Delegation Pattern  
**REJECTED**: Monolithic Command Approach

#### Rationale:
- **Consistency**: Follows established `/issue:*` command → `github-issues-workflow` agent pattern
- **Testability**: Component isolation allows targeted testing of similarity algorithms
- **Context Management**: Prevents verbose duplicate analysis from polluting main conversation
- **Error Isolation**: Agent boundaries contain GitHub API failures and rate limiting issues

#### Security Implications:
```bash
# Secure agent delegation pattern
Task(github-issues-workflow): {
  operation: "analyze_duplicates",
  issue_number: $VALIDATED_INPUT,
  confidence_threshold: 0.85,
  repository: "ondrasek/ai-code-forge"  # Hardcoded for security
}
```

**Risk Mitigation**: Input validation occurs at command level before agent delegation, preventing command injection through issue numbers or search terms.

### 2. DUPLICATE DETECTION ALGORITHM DECISION

**CHOSEN**: Hybrid Keyword + Content Similarity (Jaccard + TF-IDF)  
**REJECTED**: Semantic Similarity (BERT/ML models), Simple Keyword Matching

#### Multi-Factor Confidence Scoring:
```bash
final_confidence = (
    title_similarity * 0.40 +     # Highest weight - titles are most specific
    body_similarity * 0.30 +      # Content analysis for context
    label_overlap * 0.20 +        # Label consistency indicates similar type
    recency_factor * 0.10         # Recent issues more likely duplicates
)

# Conservative thresholds based on research
HIGH_CONFIDENCE = 0.85    # Auto-suggest with 3-day review
MEDIUM_CONFIDENCE = 0.70  # Manual review recommended  
LOW_CONFIDENCE = 0.55     # Mention but don't flag
```

#### Technical Implementation:
```bash
# Efficient similarity calculation in bash
calculate_jaccard_similarity() {
    local text1_words=$(extract_keywords "$1")
    local text2_words=$(extract_keywords "$2")
    
    # Use bash arrays for set operations
    local intersection=$(comm -12 <(echo "$text1_words" | sort) <(echo "$text2_words" | sort) | wc -l)
    local union=$(cat <(echo "$text1_words") <(echo "$text2_words") | sort -u | wc -l)
    
    # Avoid division by zero
    if [ "$union" -eq 0 ]; then echo "0.0"; else
        echo "scale=3; $intersection / $union" | bc
    fi
}
```

#### Rationale for Lightweight Approach:
- **Zero Dependencies**: Pure bash + GitHub CLI maintains deployment simplicity
- **Predictable Performance**: O(n²) complexity acceptable for typical repository sizes (< 1000 issues)
- **False Positive Control**: Conservative thresholds (85%) minimize incorrect duplicate flagging
- **Maintainability**: Simple algorithms easy to debug and improve incrementally

### 3. USER INTERACTION MODEL DECISION

**CHOSEN**: Semi-Automated with 3-Day Review Period  
**REJECTED**: Fully Automated Closure, Immediate Manual Review

#### Workflow Design:
```
Issue Detection → Similarity Analysis → Comment with Suggestions → 3-Day Review → Auto-Close or Manual Override
```

#### Comment Template Strategy:
```markdown
## 🔄 Potential Duplicate Issues Detected

**High Confidence Matches (≥85%)**:
- #123: "Similar error handling issue" (89% similarity)
- #145: "Authentication error pattern" (87% similarity)

**Review Instructions**:
- Add `not-duplicate` label if this is NOT a duplicate
- This issue will auto-close in 3 days without action
- Manual review overrides all automatic actions

**Detection Confidence**: Based on title similarity (40%), content analysis (30%), label overlap (20%), recency (10%)
```

#### Rationale:
- **User Trust**: 3-day review period prevents hasty closures
- **Clear Override**: Simple label-based override mechanism (`not-duplicate`)
- **Transparency**: Users see exactly why issues were flagged as duplicates
- **Fallback Safety**: No action taken without explicit opportunity for human intervention

### 4. TECHNICAL IMPLEMENTATION STRATEGY DECISION

**CHOSEN**: Pure Bash + GitHub CLI with Rate Limiting Management  
**REJECTED**: Python Hybrid, Direct API Calls, In-Memory State

#### Rate Limiting Strategy:
```bash
# Conservative request budgeting based on research findings
MAX_REQUESTS_PER_MINUTE=25  # Buffer below 30/min limit
BATCH_SIZE=10               # Process issues in batches
DELAY_BETWEEN_BATCHES=15    # Seconds between batch operations

# Circuit breaker for API protection
if [[ $consecutive_failures -ge 3 ]]; then
    echo "Multiple API failures detected, pausing operations..."
    sleep 300  # 5-minute cooldown
fi
```

#### Error Handling Framework:
```bash
# Three-tier error handling
handle_github_error() {
    case $exit_code in
        0) return 0 ;;                                    # Success
        1) if [[ "$output" =~ "rate limit" ]]; then       # Rate limit
               implement_backoff_delay
               return 2  # Retry signal
           fi ;;
        4) echo "Authentication required: gh auth login" ;;  # Auth failure
        *) echo "Unexpected error: $output" ;;               # Unknown error
    esac
}
```

#### Security Hardening:
```bash
# Input sanitization for all user inputs
sanitize_issue_number() {
    local input="$1"
    if [[ ! "$input" =~ ^[0-9]+$ ]]; then
        echo "Error: Invalid issue number format" >&2
        return 1
    fi
    echo "$input"
}

# Prevent command injection in search terms
sanitize_search_terms() {
    local input="$1"
    # Remove shell metacharacters
    echo "$input" | sed 's/[;&|`$(){}[\]\\]//g' | tr -d '\n\r'
}
```

## RISK ANALYSIS AND MITIGATION

### 1. Security Risks

**HIGH RISK**: Command Injection via Issue Numbers/Search Terms
- **Mitigation**: Strict input validation with regex patterns
- **Implementation**: All inputs sanitized before GitHub CLI calls

**MEDIUM RISK**: GitHub Token Exposure in Logs
- **Mitigation**: Use GitHub CLI's built-in credential management
- **Implementation**: Never log or echo GitHub CLI authentication details

**LOW RISK**: Rate Limit Exhaustion
- **Mitigation**: Conservative request budgeting with circuit breaker
- **Implementation**: 25 requests/minute with exponential backoff

### 2. False Positive Management

**Template Similarity Problem**:
```bash
# Detect issue template usage
detect_template_usage() {
    local issue_body="$1"
    # Look for template markers
    if echo "$issue_body" | grep -q "## Description\|## Expected Behavior\|## Steps to Reproduce"; then
        # Reduce body similarity weight for template issues
        body_weight=0.15  # Reduced from 0.30
        template_detected=true
    fi
}
```

**Semantic Drift Handling**:
```bash
# Time-based relevance scoring
calculate_recency_factor() {
    local issue_date="$1"
    local current_date=$(date +%s)
    local issue_timestamp=$(date -d "$issue_date" +%s)
    local days_old=$(( (current_date - issue_timestamp) / 86400 ))
    
    # Reduce confidence for old issues (>90 days)
    if [ $days_old -gt 90 ]; then
        echo "0.5"  # 50% recency factor
    else
        echo "1.0"  # Full recency factor
    fi
}
```

### 3. Performance and Scalability

**GitHub API Rate Limiting**:
- **Current Limit**: 5,000 requests/hour (authenticated)
- **Our Budget**: 25 requests/minute (1,500/hour) for safety margin
- **Batch Processing**: Process 10 issues per batch to minimize API calls

**Computational Complexity**:
- **Issue Comparison**: O(n²) for exhaustive comparison
- **Optimization**: Skip closed issues older than 6 months
- **Early Termination**: Stop at first 3 high-confidence matches

### 4. User Experience Concerns

**False Positive Communication**:
```markdown
**Not a Duplicate?** If this issue represents a different problem:
1. Add the `not-duplicate` label
2. Explain the difference in a comment
3. This will prevent auto-closure and improve our detection
```

**Clear Override Mechanism**:
- Simple label-based override (`not-duplicate`)
- Manual comment option for complex cases
- Immediate override recognition (no delays)

## INTEGRATION WITH EXISTING CODEBASE

### Command Structure Integration
```
.claude/commands/issue/dedupe.md  # New command following existing pattern
├── Delegates to github-issues-workflow agent
├── Follows argument validation pattern
└── Returns structured output to user
```

### Agent Extension Pattern
```bash
# Extend existing github-issues-workflow agent
case "$operation" in
    "analyze_duplicates")
        analyze_duplicates "$issue_number" "$confidence_threshold"
        ;;
    "create"|"update"|"review")  # Existing operations
        # ... existing logic
        ;;
esac
```

### Error Handling Consistency
- Uses same validation functions as existing issue commands
- Follows established GitHub CLI error handling patterns
- Maintains consistent user messaging format

### Label System Integration
```bash
# Use existing dynamic label discovery pattern
AVAILABLE_LABELS=$(gh label list --repo ondrasek/ai-code-forge --json name --jq '.[].name')

# Check for override label existence
if echo "$AVAILABLE_LABELS" | grep -q "not-duplicate"; then
    # Label exists, proceed with override check
else
    # Create label if it doesn't exist (one-time setup)
    gh label create "not-duplicate" --color "28a745" --description "Override duplicate detection"
fi
```

## TESTING STRATEGY

### 1. Unit Testing Approach
```bash
# Test similarity calculation functions
test_jaccard_similarity() {
    local result=$(calculate_jaccard_similarity "test words" "test words")
    assert_equals "1.000" "$result"
}

# Test input sanitization
test_input_sanitization() {
    local result=$(sanitize_issue_number "123; rm -rf /")
    assert_equals "123" "$result"
}
```

### 2. Integration Testing
```bash
# Mock GitHub CLI for testing
gh() {
    case "$1 $2" in
        "issue view") echo '{"title":"Test Issue","body":"Test content"}' ;;
        "issue list") echo '[{"number":123,"title":"Similar Issue"}]' ;;
        *) return 1 ;;
    esac
}

# Test full workflow
test_duplicate_detection_workflow() {
    result=$(analyze_duplicates 456 0.85)
    assert_contains "$result" "High Confidence Matches"
}
```

### 3. Security Testing
```bash
# Test command injection prevention
test_command_injection_prevention() {
    local malicious_input="123; curl evil.com"
    local result=$(sanitize_issue_number "$malicious_input")
    assert_not_contains "$result" "curl"
}

# Test rate limiting behavior
test_rate_limit_handling() {
    # Mock rate limit response
    export MOCK_RATE_LIMITED=true
    result=$(safe_gh_api_call issue list)
    assert_equals "2" "$?"  # Should return retry code
}
```

## MONITORING AND OBSERVABILITY

### Success Metrics
- **Duplicate Detection Rate**: Percentage of actual duplicates identified
- **False Positive Rate**: Percentage of incorrectly flagged issues
- **User Override Rate**: How often users use `not-duplicate` label
- **API Request Efficiency**: Requests per successful duplicate detection

### Logging Strategy
```bash
# Structured logging for analysis
log_duplicate_analysis() {
    local timestamp=$(date --iso-8601=seconds)
    local log_entry="{
        \"timestamp\": \"$timestamp\",
        \"operation\": \"duplicate_detection\",
        \"issue_number\": $issue_number,
        \"matches_found\": $matches_count,
        \"highest_confidence\": $max_confidence,
        \"api_requests_used\": $request_count
    }"
    echo "$log_entry" >> /var/log/claude-code/duplicate-detection.log
}
```

### Error Tracking
```bash
# Track and report errors for improvement
track_error() {
    local error_type="$1"
    local context="$2"
    echo "$(date --iso-8601=seconds) ERROR $error_type: $context" >> /var/log/claude-code/errors.log
    
    # Alert on critical errors
    if [[ "$error_type" == "AUTH_FAILURE" ]] || [[ "$error_type" == "RATE_LIMIT_EXCEEDED" ]]; then
        echo "Critical error detected: $error_type" >&2
    fi
}
```

## DEPLOYMENT PLAN

### Phase 1: Core Implementation
**High Priority**: Implement basic duplicate detection command
- Create `/issue:dedupe` command file
- Implement similarity calculation functions
- Add basic error handling and input validation
- Test with manual issue comparisons

### Phase 2: Agent Integration  
**High Priority**: Integrate with github-issues-workflow agent
- Extend agent to handle duplicate detection operations
- Implement structured output format
- Add comprehensive error handling
- Test agent delegation workflow

### Phase 3: Comment Automation
**Medium Priority**: Implement automated comment system
- Design comment template with clear user instructions
- Implement 3-day review period logic
- Add override label detection
- Test comment update and deletion workflows

### Phase 4: Rate Limiting and Optimization
**Medium Priority**: Add production-grade reliability
- Implement circuit breaker pattern
- Add exponential backoff for API failures
- Optimize batch processing for large repositories
- Add comprehensive logging and monitoring

### Phase 5: Advanced Features
**Low Priority**: Enhance detection capabilities (depends on success of Phase 1-4)
- Improve similarity algorithms based on real-world usage
- Add cross-repository duplicate detection (if requested)
- Implement machine learning enhancements (if justified by usage)
- Add integration with GitHub Actions for automatic processing

## DECISION VALIDATION

### Why Not Semantic Similarity (BERT/ML)?
1. **Complexity**: Requires Python runtime and ML dependencies
2. **Deployment**: Breaks current zero-dependency deployment model
3. **Maintenance**: Adds model versioning and update complexity
4. **Performance**: Current lightweight approach adequate for repository size

### Why Not Real-Time Processing?
1. **API Pressure**: Would exceed rate limits with active repositories
2. **Performance**: Batch processing more efficient for similarity analysis
3. **User Experience**: 3-day review period provides better user control
4. **Resource Usage**: Batch processing more predictable and manageable

### Why Not Fully Automated Closure?
1. **User Trust**: Risk of closing legitimate issues destroys user confidence
2. **Error Recovery**: Manual review period allows error correction
3. **Edge Cases**: Complex similarity cases require human judgment
4. **Safe Failure**: Conservative approach protects against algorithmic errors

## SUCCESS CRITERIA

### Technical Success Metrics
- **Zero Security Incidents**: No command injection or authentication issues
- **95%+ Uptime**: Robust error handling prevents command failures
- **<30 API Requests/Minute**: Stays within conservative rate limits
- **<5% False Positive Rate**: Maintains user trust through conservative detection

### User Experience Success Metrics
- **Clear Override Path**: Users can easily override incorrect detections
- **Transparent Process**: Users understand why issues were flagged as duplicates
- **Timely Notification**: 3-day review period provides adequate response time
- **Minimal Manual Overhead**: Automation reduces manual duplicate management

### Operational Success Metrics
- **Seamless Integration**: Works with existing command and agent patterns
- **Maintainable Code**: Clear, testable functions following codebase conventions
- **Comprehensive Documentation**: Complete command documentation and usage examples
- **Effective Testing**: Unit and integration tests prevent regressions

---

**Final Recommendation**: Proceed with agent-delegated, semi-automated duplicate detection using conservative similarity thresholds and comprehensive user override mechanisms. This approach balances automation benefits with user trust and system reliability requirements while maintaining consistency with existing codebase patterns and deployment constraints.