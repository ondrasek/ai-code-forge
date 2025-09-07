---
description: Comprehensive code refactoring for structure, performance, and maintainability.
argument-hint: Optional FILES to refactor, or empty to analyze entire codebase.
allowed-tools: Task, Read, Edit, MultiEdit, Bash, Grep
---

# Code Refactoring

!`git status`
!`git diff --name-only`

Comprehensive code refactoring focusing on structure, performance, and maintainability for full codebase or specified files.

## Instructions

1. Parse $ARGUMENTS for refactoring parameters:
   - --pattern [extract-method|extract-class|inline|rename]
   - --focus [performance|readability|structure|patterns]
   - --safe (backward-compatible only)
   - --dry-run (preview changes)
   - --incremental (confirm each change)
   - --max-changes N
   - FILES... (specific files to refactor)

2. Execute enhanced parallel analysis clusters for comprehensive refactoring
1. coordinate enhanced parallel analysis clusters for comprehensive refactoring:
   - **Pattern Analysis Cluster**: patterns + researcher + context + critic (find duplication with researcher validation)
   - **Architecture Quality Cluster**: principles + constraint-solver + stack-advisor + code-cleaner (check SOLID with design integrity)
   - **Dependency Mapping Cluster**: constraint-solver + conflicts + context + stack-advisor (map dependencies with conflict resolution)
   - **Performance Analysis Cluster**: performance-optimizer + patterns + critic + constraint-solver (identify optimization opportunities)
2. generate comprehensive refactoring plan validated by conflicts + principles + critic agents
3. apply changes incrementally with test-strategist + code-cleaner + stack-advisor validation at each step
4. invoke code-cleaner agent: micro-improvements coordinated with principles + critic agents
5. invoke code-cleaner agent: verify completeness with patterns + test-strategist validation
6. run comprehensive tests with test-strategist + performance-optimizer coordination
7. invoke stack-advisor agent: update documentation with code-cleaner + principles validation

PARAMETERS:
--pattern [extract-method|extract-class|inline|rename]
--focus [performance|readability|structure|patterns]
--safe (backward-compatible only)
--dry-run (preview changes)
--incremental (confirm each change)
--max-changes N
FILES... (specific files to refactor)

ENHANCED_AGENT_CLUSTERS (CLAUDE.md compliant 3+ agents per cluster):
Pattern Analysis: patterns + researcher + context (3 agents)
Architecture Quality: principles + constraint-solver + stack-advisor (3 agents)
Dependency Mapping: constraint-solver + conflicts + context (3 agents)
Performance Analysis: performance-optimizer + patterns + critic (3 agents)
Implementation Excellence: code-cleaner + patterns + test-strategist (3 agents)
Quality Assurance: critic + test-strategist + performance-optimizer (3 agents)
Documentation: stack-advisor + principles + code-cleaner (3 agents)
Validation: options-analyzer + conflicts + test-strategist (3 agents)
Coordination: All enhanced clusters execute in parallel via single message with multiple Task() calls (CLAUDE.md mandatory protocol)

REFACTORING_PATTERNS:
- extract method/class
- replace conditional with polymorphism
- introduce parameter object
- remove duplication
- simplify complex conditionals

OUTPUT:
- refactoring opportunities count
- complexity reduction estimate
- specific changes by category
- breaking changes warnings
- phased implementation plan

```
## Refactoring Analysis Report

**Files Analyzed**: 23
**Refactoring Opportunities**: 47
**Estimated Improvement**: 35% reduction in complexity

### Pattern Detection (patterns agent)

1. **Duplicate Authentication Logic**
   - Found in: 5 files
   - Lines saved: ~120
   - Recommendation: Extract to AuthenticationService
   ```python
   # Before (repeated in 5 places)
   def verify_user(token):
       decoded = jwt.decode(token, SECRET)
       user = db.get_user(decoded['id'])
       if not user or not user.active:
           raise AuthError()
       return user
   
   # After (single implementation)
   class AuthenticationService:
       def verify_user(self, token: str) -> User:
           # Centralized implementation
   ```

2. **Data Validation Pattern**
   - Found in: 8 endpoints
   - Recommendation: Use decorator pattern

### SOLID Violations (principles agent)

1. **Single Responsibility Violation**
   - File: `src/services/user_service.py`
   - Issue: UserService handles auth, data, and email
   - Fix: Split into UserService, AuthService, EmailService

2. **Open/Closed Violation**
   - File: `src/processors/data_processor.py`
   - Issue: Switch statement for types
   - Fix: Use strategy pattern

### Performance Improvements (performance-optimizer agent)

1. **N+1 Query Problem**
   - Location: `src/api/list_users.py`
   - Impact: 100+ DB queries per request
   - Solution: Use eager loading
   ```python
   # Before
   users = User.query.all()
   for user in users:
       user.profile  # Triggers query
   
   # After
   users = User.query.options(joinedload('profile')).all()
   ```

### Micro-Improvements Applied (code-cleaner agent)

- Renamed 47 variables for clarity
- Added type hints to 23 functions
- Removed 12 unused imports
- Fixed 18 inconsistent indentations
- Simplified 9 boolean expressions

### Refactoring Plan

1. **Phase 1**: Extract shared authentication (2 hours)
2. **Phase 2**: Implement service layer pattern (4 hours)
3. **Phase 3**: Optimize database queries (2 hours)
4. **Phase 4**: Apply micro-improvements (1 hour)

### Breaking Changes

⚠️ **API Changes Required**:
- `UserService.authenticate()` → `AuthService.authenticate()`
- Database schema migration needed for query optimization
```

## Parameters

- `--pattern <type>`: Apply specific refactoring pattern
  - `extract-method`, `extract-class`, `inline`, `rename`
- `--focus <area>`: Focus on specific aspect
  - `performance`, `readability`, `structure`, `patterns`
- `--safe`: Only backward-compatible changes
- `--dry-run`: Show what would be changed without applying
- `--incremental`: Apply changes one at a time with confirmation
- `--max-changes <n>`: Limit number of changes

## Refactoring Patterns Library

### Extract Method
```python
# Before
def process_order(order):
    # 50 lines of validation logic
    # 30 lines of calculation logic
    # 20 lines of notification logic

# After
def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    send_notifications(order, total)
```

### Replace Conditional with Polymorphism
```python
# Before
if shape_type == "circle":
    area = 3.14 * radius ** 2
elif shape_type == "square":
    area = side ** 2

# After
class Shape(ABC):
    @abstractmethod
    def area(self): pass

class Circle(Shape):
    def area(self):
        return 3.14 * self.radius ** 2
```

### Introduce Parameter Object
```python
# Before
def create_user(name, email, age, address, phone):
    # ...

# After
@dataclass
class UserData:
    name: str
    email: str
    age: int
    address: str
    phone: str

def create_user(user_data: UserData):
    # ...
```

## Agent Integration

**Enhanced Advanced Multi-Cluster Coordination**:

**Pattern Analysis Cluster** (patterns + researcher + context + critic):
- Comprehensive code pattern analysis with researcher validation and architectural context
- Critical assessment of pattern effectiveness and design quality evaluation
- Deep system understanding across entire codebase with researcher-backed insights

**Architecture Quality Cluster** (principles + constraint-solver + stack-advisor + conflicts):
- Architectural principle validation with constraint-aware design integrity and conflict resolution
- Technology-specific guidance ensuring appropriate principle application
- Systematic constraint navigation with comprehensive conflict resolution

**Dependency Mapping Cluster** (constraint-solver + conflicts + context + stack-advisor):
- Multi-dimensional dependency analysis with constraint-aware solutions
- System context understanding and technology-specific dependency guidance
- Conflict resolution in complex dependency relationships with architectural awareness

**Performance Analysis Cluster** (performance-optimizer + patterns + critic + constraint-solver):
- Performance bottleneck analysis with pattern recognition and critical assessment
- Optimization strategies within resource constraints and design limitations
- Systematic performance pattern analysis with constraint-aware validation

**Implementation Excellence Cluster** (code-cleaner + patterns + test-strategist + principles):
- Code quality improvements with pattern recognition and principle compliance
- Comprehensive testing integration with quality assurance and principle adherence
- Technology-aware code refinement ensuring optimal principle-based implementations

**Quality Assurance Cluster** (critic + test-strategist + performance-optimizer + code-cleaner):
- Critical evaluation with comprehensive testing and performance validation
- Code quality optimization with systematic risk assessment
- Multi-dimensional quality metrics tracking and improvement validation

**Documentation Cluster** (stack-advisor + principles + code-cleaner + context):
- Technology-specific documentation with architectural context and principle compliance
- Repository-level guideline compliance with code quality integration
- Principle-based documentation standards with comprehensive system understanding

**Validation Cluster** (options-analyzer + conflicts + test-strategist + critic):
- Alternative approach exploration with systematic testing validation
- Comprehensive conflict resolution with critical assessment and testing integration
- Multi-option analysis with risk-aware validation and testing coverage

**Enhanced Memory-Coordinated Integration**: Leverages historical refactoring outcomes through researcher + context agents for optimized decision-making with comprehensive validation by critic + principles + conflicts agents

## Memory Integration

**Before Refactoring**: Use `mcp__memory__search_nodes()` to check for:
- Previous refactoring outcomes and effectiveness patterns
- Historical code quality improvements and architectural decisions
- Team-specific refactoring preferences and successful approaches
- Pattern-specific refactoring strategies and their long-term impact

**After Refactoring**: Store findings with `mcp__memory__create_entities()` and `mcp__memory__create_relations()`:
- Refactoring pattern effectiveness and code quality improvements
- Architectural decision outcomes and maintainability impact
- Team learning patterns and successful refactoring strategies
- Cross-domain relationships between refactoring and system performance

## Related Commands

- `/review` - Comprehensive code review with parallel agent clusters before refactoring
- `/test` - Ensure comprehensive test coverage with testing agent coordination
- `/security` - Security impact analysis with security specialist agents
- `/agents-audit` - Analyze refactoring process effectiveness and agent coordination

## Best Practices

1. **Always run tests** before and after refactoring
2. **Refactor incrementally** - small, tested changes
3. **Preserve behavior** - refactoring shouldn't change functionality
4. **Document changes** - especially breaking changes
5. **Use version control** - commit before major refactoring
6. **Measure impact** - track complexity metrics
7. **Get review** - have changes reviewed by team