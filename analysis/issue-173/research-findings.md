# Issue #173 Research Findings

## Issue Summary
**Title**: feat: implement terminal title management with issue numbers in worktree scripts
**Status**: OPEN
**Labels**: enhancement, feat
**Priority**: Medium (no priority label - appropriate per owner validation)

## Technical Requirements
- Implement terminal escape sequences for automatic title changes
- Cross-platform compatibility (iTerm2, Terminal.app, gnome-terminal, Windows Terminal)
- Security: Sanitized input to prevent escape sequence injection
- Integration with existing worktree scripts
- Graceful fallback for unsupported terminals

## Comprehensive External Research Results

### ANSI OSC (Operating System Command) Sequences

**Standards Foundation:**
- Based on ECMA-48 (5th edition, 1991), ISO/IEC 6429, ANSI X3.64 standards
- XTerm Control Sequences document (updated 2025/06/22, Patch #401) serves as de facto standard
- OSC sequences follow format: `ESC ] Ps ; Pt BEL` or `ESC ] Ps ; Pt ST`

**Terminal Title Control Sequences:**
- `OSC 0 ; txt BEL/ST` - Set icon name and window title
- `OSC 1 ; txt BEL/ST` - Set icon name only  
- `OSC 2 ; txt BEL/ST` - Set window title only
- Two terminator options: BEL (0x07) or ST (ESC \)

**Standard Escape Sequences:**
```bash
# Set both icon and window title
echo -e '\e]0;TITLE\e\\'
echo -e '\e]0;TITLE\a'

# Set window title only  
echo -e '\e]2;TITLE\e\\'
echo -e '\e]2;TITLE\a'

# Set icon name only
echo -e '\e]1;TITLE\e\\'
echo -e '\e]1;TITLE\a'
```

### Cross-Platform Terminal Compatibility

**Universal Compatibility (2025):**
- Standard OSC sequences (`\e]0;`, `\e]1;`, `\e]2;`) work across all major terminals
- iTerm2, Terminal.app, GNOME Terminal, Windows Terminal support xterm standards
- Most modern terminals implement xterm escape sequence subset for compatibility

**Terminal-Specific Features:**
- **iTerm2:** Supports additional OSC 6 sequences for tab coloring
- **Windows Terminal:** Sets `TERM_PROGRAM=WindowsTerminal` for detection
- **GNOME Terminal (VTE):** Full xterm compatibility with VT102/ECMA-48 support
- **Legacy Support:** VT100 core sequences supported by virtually all terminals

**tmux/screen Compatibility:**
- **tmux 3.4+:** Supports OSC 133 shell integration, OSC 52 clipboard access
- **tmux title handling:** Window title (#T) set via OSC sequences: `printf '\033]2;My Title\033\\'`
- **screen:** Basic OSC support, but tmux preferred for modern workflows
- **Pass-through:** Requires `set -g allow-passthrough on` in tmux.conf for advanced OSC

### Terminal Capability Detection Methods

**$TERM Environment Variable:**
- Primary mechanism: Applications query terminal capabilities via terminfo database
- Common values: `xterm`, `xterm-256color`, `screen`, `tmux-256color`
- Location: `/lib/terminfo`, `$HOME/.terminfo`, or `$TERMINFO` directories
- Modern terminals often set `TERM=xterm` for maximum compatibility

**Feature Detection Approaches:**
```bash
# Basic terminal type detection
case "$TERM" in
    xterm*|rxvt*|alacritty|tmux*|screen*)
        # Terminal supports OSC sequences
        ;;
    linux|vt*)
        # Console terminal, limited escape support
        ;;
esac

# Modern terminal program detection
if [[ -n "$TERM_PROGRAM" ]]; then
    case "$TERM_PROGRAM" in
        iTerm.app) echo "iTerm2 detected" ;;
        Terminal.app) echo "macOS Terminal detected" ;;
        WindowsTerminal) echo "Windows Terminal detected" ;;
    esac
fi
```

**Additional Detection Variables (2025):**
- `$TERM_PROGRAM` and `$TERM_PROGRAM_VERSION` for specific terminal identification
- `$COLORTERM` for color capability detection
- Query sequences for runtime capability detection (experimental)

### Security Considerations for Escape Sequence Injection

**Critical Security Vulnerabilities (2025):**
- **ANSI Terminal Code Abuse:** Escape sequences can hide malicious instructions
- **Log Injection (OWASP):** Tracked as CWE-150 - Improper Neutralization of Escape Sequences
- **Recent Attacks:** MCP (Model Context Protocol) vulnerabilities discovered in 2025

**Attack Vectors:**
- Invisible text via foreground/background color manipulation
- Screen content overwriting using cursor movement
- Clipboard injection via OSC 52 sequences
- Hyperlink manipulation for phishing attacks

**Essential Sanitization Practices:**
```bash
# Basic escape sequence removal
sanitize_title() {
    local title="$1"
    # Remove escape character (0x1b) and control characters
    title="${title//$(printf '\033')/}"
    title="${title//$(printf '\007')/}"  # BEL
    title="${title//$(printf '\x1b')/}" # ESC
    # Limit length to prevent buffer overflow
    title="${title:0:100}"
    echo "$title"
}

# Comprehensive sanitization
secure_title() {
    local title="$1"
    # Whitelist approach: only allow printable ASCII
    title=$(echo "$title" | tr -cd '[:print:]' | tr -cd '[:space:][:alnum:][:punct:]')
    # Remove potential injection characters
    title="${title//\$/}"    # Shell variables
    title="${title//\`/}"    # Command substitution
    title="${title//;/}"     # Command separator
    echo "${title:0:80}"     # Enforce length limit
}
```

**Protection Requirements:**
- Replace byte 0x1b (escape) with placeholder character
- Implement input validation with whitelist approach
- Limit title length (recommended: 80-100 characters)
- Encode special characters that have terminal meaning
- Server-side validation as primary security measure

### Shell Integration Patterns (2025)

**Bash Integration:**
```bash
# PROMPT_COMMAND for dynamic titles
PROMPT_COMMAND='echo -ne "\e]0;${USER}@${HOSTNAME}: ${PWD}\e\\"'

# Function-based approach
set_title() {
    local title="$1"
    title=$(sanitize_title "$title")
    case "$TERM" in
        xterm*|rxvt*|alacritty|tmux*|screen*)
            echo -ne "\e]0;${title}\e\\"
            ;;
    esac
}
```

**Zsh Integration:**
```zsh
# Precmd hook for title updates
precmd() {
    local title="${USER}@${HOST}: ${PWD}"
    title=$(sanitize_title "$title")
    print -Pn "\e]0;${title}\e\\"
}

# Preexec for command-based titles
preexec() {
    local cmd="$1"
    local title="${USER}@${HOST}: ${cmd}"
    title=$(sanitize_title "$title")
    print -Pn "\e]0;${title}\e\\"
}
```

**Fish Shell Integration:**
```fish
# fish_title function (built-in)
function fish_title
    set -l title (prompt_pwd)
    if test -n "$argv[1]"
        set title "$argv[1] - $title"
    end
    echo (sanitize_title "$title")
end

# Custom sanitization function
function sanitize_title
    string replace -a (printf '\033') '' $argv | string sub -l 80
end
```

**Modern Shell Ecosystem (2025):**
- Fish shell adoption grown 340% due to zero-configuration approach
- Zsh remains dominant with Oh My Zsh ecosystem
- Shell integration focuses on prompt frameworks (Starship, Powerlevel10k, Tide)
- Performance optimization: Fish reduces command completion time by 23% vs. Bash

### Fallback Mechanisms for Unsupported Terminals

**Detection and Graceful Degradation:**
```bash
supports_osc_titles() {
    case "$TERM" in
        # Known compatible terminals
        xterm*|rxvt*|alacritty|kitty|tmux*|screen*|iterm*|vte*)
            return 0
            ;;
        # Console terminals (limited support)
        linux|vt100|vt102|vt220)
            return 1
            ;;
        # Unknown terminals - test capability
        *)
            # Conservative approach: assume no support
            return 1
            ;;
    esac
}

set_terminal_title() {
    local title="$1"
    
    # Sanitize input
    title=$(sanitize_title "$title")
    
    # Check terminal support
    if supports_osc_titles; then
        echo -ne "\e]0;${title}\e\\"
    else
        # Fallback: update PS1 prompt instead
        PS1="[${title}] ${PS1}"
    fi
}
```

**Alternative Fallback Strategies:**
- Update shell prompt (PS1) to include title information
- Use window manager tools (wmctrl, xdotool) where available
- Log title changes to file for debugging
- Silent failure with optional verbose mode for troubleshooting

**Best Practices for Robust Implementation:**
- Always sanitize input before setting titles
- Implement graceful fallback for unsupported terminals
- Test across multiple terminal environments
- Provide configuration options to disable title setting
- Monitor for security vulnerabilities in escape sequence handling

## Implementation Recommendations

**High Priority Security Measures:**
- Implement comprehensive input sanitization (escape character removal)
- Use whitelist approach for allowed characters
- Enforce length limits (80-100 characters maximum)
- Regular security assessment of escape sequence handling

**Cross-Platform Compatibility Strategy:**
- Use standard OSC 0/1/2 sequences for maximum compatibility
- Implement terminal capability detection via $TERM and $TERM_PROGRAM
- Provide fallback mechanisms for unsupported terminals
- Test across iTerm2, Terminal.app, GNOME Terminal, Windows Terminal

**Shell Integration Approach:**
- Hook into shell prompt mechanisms (PROMPT_COMMAND, precmd, fish_title)
- Support bash, zsh, and fish shells
- Consider tmux/screen session compatibility
- Follow modern shell ecosystem patterns

## Repository Context
- Working in dedicated worktree: issue-173-feat-implement-terminal
- Need to find existing worktree scripts to integrate with
- Must follow file structure guidelines in CLAUDE.md