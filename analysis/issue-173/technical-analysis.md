# Issue #173 Technical Analysis

## Technology Context
**Files**: Shell scripts (*.sh) for worktree management
**Technologies**: Bash Shell Scripting + Terminal Integration
**Context**: Implementing terminal title management with issue numbers

## Current Codebase Patterns

### Existing Shell Script Standards
Based on analysis of `/scripts/worktree/worktree.sh`:

**Established Patterns:**
- `#!/bin/bash` shebang with strict error handling: `set -euo pipefail`
- POSIX-compliant variable expansion: `"$(dirname "${BASH_SOURCE[0]}")"`
- Robust error handling with colored output functions
- Consistent exit codes and error reporting
- Modular script architecture with command delegation

**Current Color/Terminal Usage:**
```bash
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
```

## Shell Scripting Technology Guidelines

### MANDATORY Requirements

#### 1. Cross-Platform Compatibility
**ENFORCE**: POSIX compliance for maximum portability
- Use `#!/bin/bash` for bash-specific features, `#!/bin/sh` for POSIX
- Avoid bashisms when targeting sh: `[[ ]]` → `[ ]`, `${var//pattern/replacement}` → `sed`
- Test on multiple shells: bash, zsh, dash, sh

**Platform-Specific Considerations:**
- **macOS**: BSD utilities vs GNU utilities (`sed -i ''` vs `sed -i`)
- **Windows**: Git Bash, WSL, PowerShell compatibility
- **Linux**: Various distributions with different default shells

#### 2. Terminal Escape Sequence Security
**CRITICAL**: Input sanitization to prevent injection attacks

```bash
# SECURE: Sanitize input before terminal output
sanitize_terminal_input() {
    local input="$1"
    # Remove control characters except safe ones
    printf '%s' "$input" | tr -d '\001-\010\013\014\016-\037\177'
}

# SECURE: Set terminal title safely
set_terminal_title() {
    local title="$1"
    local sanitized_title
    sanitized_title=$(sanitize_terminal_input "$title")
    
    # Limit length to prevent buffer overflow
    if [ ${#sanitized_title} -gt 100 ]; then
        sanitized_title="${sanitized_title:0:97}..."
    fi
    
    printf '\033]0;%s\007' "$sanitized_title"
}
```

#### 3. Terminal Capability Detection
**MANDATORY**: Detect terminal capabilities before using escape sequences

```bash
# Terminal capability detection
is_terminal_capable() {
    # Check if stdout is a terminal
    [ -t 1 ] || return 1
    
    # Check TERM environment variable
    case "$TERM" in
        *xterm*|*color*|screen*|tmux*|rxvt*|ansi) return 0 ;;
        dumb|unknown) return 1 ;;
        *) 
            # Test with tput if available
            if command -v tput >/dev/null 2>&1; then
                tput colors >/dev/null 2>&1 && [ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]
            else
                return 1
            fi
            ;;
    esac
}

# Safe escape sequence wrapper
safe_escape() {
    if is_terminal_capable; then
        printf '%s' "$1"
    fi
}
```

#### 4. Error Handling and Fallback Mechanisms
**REQUIRED**: Graceful degradation when terminal features unavailable

```bash
# Follow existing error handling pattern from worktree.sh
set -euo pipefail

# Error reporting (existing pattern)
print_error() { echo -e "${RED}ERROR:${NC} $1" >&2; }
print_success() { echo -e "${GREEN}SUCCESS:${NC} $1"; }

# Enhanced with terminal capability checks
safe_print_error() {
    if is_terminal_capable; then
        echo -e "${RED}ERROR:${NC} $1" >&2
    else
        echo "ERROR: $1" >&2
    fi
}
```

### Implementation Patterns

#### 1. OSC (Operating System Command) Sequences
**Standard Implementation:**
```bash
# Xterm standard: ESC ]0;title BEL (most widely supported)
set_xterm_title() {
    local title="$1"
    printf '\033]0;%s\007' "$title"
}

# Alternative terminator for compatibility
set_xterm_title_alt() {
    local title="$1"
    printf '\033]0;%s\033\\' "$title"
}
```

#### 2. Session Compatibility (tmux/screen)
**CRITICAL**: Handle terminal multiplexers correctly
```bash
# Detect and handle tmux/screen sessions
is_multiplexer_session() {
    [ -n "${TMUX:-}" ] || [ -n "${STY:-}" ]
}

set_title_with_multiplexer_support() {
    local title="$1"
    
    if [ -n "${TMUX:-}" ]; then
        # tmux: set window title
        printf '\033k%s\033\\' "$title"
        # Also set terminal title if supported
        printf '\033]0;%s\007' "$title"
    elif [ -n "${STY:-}" ]; then
        # screen: set window title
        printf '\033k%s\033\\' "$title"
    else
        # Direct terminal
        printf '\033]0;%s\007' "$title"
    fi
}
```

#### 3. Integration with Existing Worktree Scripts
**REQUIRED**: Follow established patterns from codebase

```bash
# Follow existing script structure pattern
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use existing color scheme and functions
source_color_functions() {
    # Reuse color definitions from worktree.sh
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
}

# Integration point for worktree operations
update_terminal_title_for_worktree() {
    local issue_number="$1"
    local branch_name="$2"
    
    if is_terminal_capable; then
        local title="Issue #${issue_number}: ${branch_name}"
        set_title_with_multiplexer_support "$title"
    fi
}
```

### Security Considerations

#### 1. Input Validation
**CRITICAL**: Prevent escape sequence injection
- Validate issue numbers are numeric: `[[ "$issue" =~ ^[0-9]+$ ]]`
- Sanitize branch names and titles
- Limit string lengths to prevent buffer overflows
- Strip dangerous control characters

#### 2. Environment Variable Safety
**MANDATORY**: Handle potentially malicious environment variables
```bash
# Validate TERM variable
validate_term_variable() {
    case "${TERM:-dumb}" in
        *[[:cntrl:]]*) TERM="dumb" ;;  # Contains control characters
        "") TERM="dumb" ;;              # Empty
        *) ;;                           # Keep as-is
    esac
}
```

### Testing Strategy

#### 1. Cross-Platform Testing
**REQUIRED**: Test matrix
- **Shells**: bash, zsh, dash, sh
- **Terminals**: iTerm2, Terminal.app, gnome-terminal, Windows Terminal, Command Prompt
- **Multiplexers**: tmux, screen
- **Environments**: macOS, Linux, Windows (Git Bash, WSL)

#### 2. Security Testing
**CRITICAL**: Validate against injection attacks
```bash
# Test cases for security validation
test_escape_injection() {
    local malicious_input='\033[H\033[2Jmalicious_clear_screen'
    local sanitized
    sanitized=$(sanitize_terminal_input "$malicious_input")
    
    # Should not contain escape sequences
    [[ "$sanitized" != *$'\033'* ]] || {
        echo "SECURITY TEST FAILED: Escape sequence not sanitized"
        return 1
    }
}
```

### Performance Considerations

#### 1. Terminal Query Optimization
**OPTIMIZATION**: Cache terminal capabilities
```bash
# Cache terminal capability detection
_terminal_capable_cache=""
is_terminal_capable_cached() {
    if [ -z "$_terminal_capable_cache" ]; then
        if is_terminal_capable; then
            _terminal_capable_cache="yes"
        else
            _terminal_capable_cache="no"
        fi
    fi
    [ "$_terminal_capable_cache" = "yes" ]
}
```

#### 2. Minimize Terminal Queries
**PERFORMANCE**: Avoid repeated capability checks during single script execution

### Integration Points

#### 1. Worktree Script Integration
**IMPLEMENTATION**: Add terminal title updates to key operations
- `worktree-create.sh`: Set title when creating worktree
- `worktree-launch.sh`: Update title when launching Claude Code
- `worktree-deliver.sh`: Set title with issue context

#### 2. Error Recovery
**ROBUSTNESS**: Handle interrupted operations
```bash
# Terminal state cleanup on script exit
cleanup_terminal_state() {
    # Reset title to default on script exit
    if is_terminal_capable; then
        printf '\033]0;Terminal\007'
    fi
}
trap cleanup_terminal_state EXIT
```

## Architecture Recommendations

### High Priority Implementation
1. **Terminal capability detection library** - Reusable across all worktree scripts
2. **Secure title setting functions** - With input sanitization and multiplexer support
3. **Integration with existing worktree operations** - Minimal changes to current architecture

### Medium Priority Enhancements  
1. **Advanced terminal feature detection** - Beyond basic ANSI support
2. **User configuration system** - Allow disabling terminal title updates
3. **Comprehensive test suite** - Automated testing across platforms

### Risk Mitigation
1. **Graceful degradation** - All functionality works without terminal title support
2. **Security-first approach** - Input sanitization prevents injection attacks
3. **Backward compatibility** - No breaking changes to existing worktree scripts

## External Dependencies

### Required Tools
- `tput` (optional, for enhanced terminal capability detection)
- Standard POSIX utilities: `printf`, `tr`, `sed`

### Environment Variables
- `TERM` - Terminal type detection
- `TMUX` - tmux session detection  
- `STY` - screen session detection
- `BASH_SOURCE` - Script directory resolution (existing pattern)

## Implementation Notes

**Follow Existing Patterns:**
- Use existing color scheme and output functions from `worktree.sh`
- Maintain modular script architecture
- Follow established error handling patterns with `set -euo pipefail`
- Use consistent command-line argument processing

**New Patterns to Establish:**
- Terminal capability detection as standard library function
- Secure escape sequence handling as reusable utility
- Title management integrated into worktree lifecycle